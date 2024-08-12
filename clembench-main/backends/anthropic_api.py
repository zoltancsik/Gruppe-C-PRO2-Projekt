from typing import List, Dict, Tuple, Any
from retry import retry
import anthropic
import backends
import json
import base64
import httpx
import imghdr

from backends.utils import ensure_messages_format

logger = backends.get_logger(__name__)

NAME = "anthropic"


class Anthropic(backends.Backend):
    def __init__(self):
        creds = backends.load_credentials(NAME)
        self.client = anthropic.Anthropic(api_key=creds[NAME]["api_key"])

    def get_model_for(self, model_spec: backends.ModelSpec) -> backends.Model:
        return AnthropicModel(self.client, model_spec)


class AnthropicModel(backends.Model):
    def __init__(self, client: anthropic.Client, model_spec: backends.ModelSpec):
        super().__init__(model_spec)
        self.client = client

    def encode_image(self, image_path):
        if image_path.startswith('http'):
            image_bytes = httpx.get(image_path).content
        else:
            with open(image_path, "rb") as image_file:
                image_bytes = image_file.read()
        image_data = base64.b64encode(image_bytes).decode("utf-8")
        image_type = imghdr.what(None, image_bytes)
        return image_data, "image/"+str(image_type)

    def encode_messages(self, messages):
        encoded_messages = []
        system_message = ''

        for message in messages:
            if message["role"] == "system":
                system_message = message["content"]
            else:

                content = list()
                content.append({
                    "type": "text",
                    "text": message["content"]
                })

                if self.model_spec.has_attr('supports_images'):
                    if "image" in message.keys():

                        if not self.model_spec.has_attr('support_multiple_images') and len(message['image']) > 1:
                            logger.info(
                                f"The backend {self.model_spec.__getattribute__('model_id')} does not support multiple images!")
                            raise Exception(
                                f"The backend {self.model_spec.__getattribute__('model_id')} does not support multiple images!")
                        else:
                            # encode each image
                            for image in message['image']:
                                encoded_image_data, image_type = self.encode_image(image)
                                content.append({
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": image_type,
                                        "data": encoded_image_data,
                                    }
                                })

                claude_message = {
                    "role": message["role"],
                    "content": content
                }
                encoded_messages.append(claude_message)


        return encoded_messages, system_message

    @retry(tries=3, delay=0, logger=logger)
    @ensure_messages_format
    def generate_response(self, messages: List[Dict]) -> Tuple[str, Any, str]:
        """
        :param messages: for example
                [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Who won the world series in 2020?"},
                    {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
                    {"role": "user", "content": "Where was it played?"}
                ]
        :return: the continuation
        """
        prompt, system_message = self.encode_messages(messages)

        completion = self.client.messages.create(
            messages=prompt,
            system=system_message,
            model=self.model_spec.model_id,
            temperature=self.get_temperature(),
            max_tokens=self.get_max_tokens()
        )

        json_output = completion.model_dump_json()
        response = json.loads(json_output)
        response_text = completion.content[0].text

        return prompt, response, response_text
