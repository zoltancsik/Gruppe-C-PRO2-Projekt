import json
import random
import string
from clemgame.clemgame import GameInstanceGenerator

GAME_NAME = 'sound_alike'
N_INSTANCES = 3
N_EPISODES = 1
SEED = 123
word = "This"  # FIXME: should be a word from word_pool.json


class SoundAlikeInstanceGenerator(GameInstanceGenerator):
    def __init__(self):
        super().__init__(GAME_NAME)

    def on_generate(self):
        prompt_a, prompt_b = (
            self.load_template(f'resources/initial_prompts/initial_prompt_{x}')
            for x in ['a', 'b']
        )

        for episode in range(N_EPISODES):
            # Here maybe add more difficulities?
            experiment = self.add_experiment(f"Episode {episode}")
            for game_id in range(N_INSTANCES):
                n_turns = random.randint(3, 5)
                instance = self.add_game_instance(experiment, game_id)
                instance['n_turns'] = n_turns

                instance['prompt_player_a'] = self.create_prompt(
                    prompt_a, word,  n_turns)
                instance['prompt_player_b'] = self.create_prompt(
                    prompt_b, word,  n_turns)

    def create_prompt(self, prompt: str, word: str, n_turns: int) -> str:
        text = string.Template(prompt).substitute(
                t_word=word,
                nturns=n_turns)
        return text

    def generate(self, filename="in/instances.json", **kwargs):
        self.on_generate(**kwargs)
        with open(filename, 'w', encoding='utf-8') as json_file:
            json.dump(self.instances, json_file, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    random.seed(SEED)
    SoundAlikeInstanceGenerator().generate()
