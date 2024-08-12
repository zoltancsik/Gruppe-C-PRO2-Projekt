from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from typing import List, Dict, Tuple, Any
from retry import retry
import json
import backends
from backends.utils import ensure_messages_format

logger = backends.get_logger(__name__)

NAME = "mistral"


class Mistral(backends.Backend):

    def __init__(self):
        creds = backends.load_credentials(NAME)
        self.client = MistralClient(api_key=creds[NAME]["api_key"])

    def list_models(self):
        models = self.client.models.list()
        names = [item.id for item in models.data]
        names = sorted(names)
        return names

    def get_model_for(self, model_spec: backends.ModelSpec) -> backends.Model:
        return MistralModel(self.client, model_spec)


class MistralModel(backends.Model):

    def __init__(self, client: MistralClient, model_spec: backends.ModelSpec):
        super().__init__(model_spec)
        self.client = client

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

        prompt = []
        for m in messages:
            prompt.append(ChatMessage(role=m['role'], content=m['content']))
        api_response = self.client.chat(model=self.model_spec.model_id,
                                        messages=prompt,
                                        temperature=self.get_temperature(),
                                        max_tokens=self.get_max_tokens())
        message = api_response.choices[0].message
        if message.role != "assistant":  # safety check
            raise AttributeError("Response message role is " + message.role + " but should be 'assistant'")
        response_text = message.content.strip()
        response = json.loads(api_response.model_dump_json())

        return messages, response, response_text
