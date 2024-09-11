import json
import random
import string
import os
from clemgame.clemgame import GameInstanceGenerator

LEVELS = ['EASY', 'MEDIUM', 'CO-OP']
GAME_NAME = 'sound_alike'
N_INSTANCES = 3
N_EPISODES = 1


class SoundAlikeInstanceGenerator(GameInstanceGenerator):
    def __init__(self):
        super().__init__(GAME_NAME)

    def on_generate(self):
        # Create Episodes
        for episode in range(N_EPISODES):
            experiment = self.add_experiment(f"Episode {episode}")

            # Create Game Instances
            for game_id in range(N_INSTANCES):

                difficulty = random.choice(LEVELS)
                first_word = self.pick_starting_word(difficulty)
                n_turns = random.choice([3, 5])

                prompt_a, prompt_b = self._load_custom_prompts(difficulty)
                instance = self.add_game_instance(experiment, game_id)
                instance['difficulty'] = difficulty
                instance['n_turns'] = n_turns
                instance['starting_word'] = first_word
                instance['points_needed'] = 10  # FIXME: Adjust?
                instance['prompt_player_a'] = self.create_prompt(
                    prompt_a, first_word,  n_turns)
                instance['prompt_player_b'] = self.create_prompt(
                    prompt_b, first_word,  n_turns)

    def _load_custom_prompts(self, difficulty):
        base_path = os.getcwd()
        if difficulty == "EASY":
            folder = "level_easy"
        elif difficulty == "MEDIUM":
            folder = "level_medium"
        elif difficulty == "CO-OP":
            folder = "level_coop"
        prompt_a, prompt_b = (
            self.load_template
            (
                # FIXME: For this you have to be in the game's folder
                f'{base_path}/resources/initial_prompts/{folder}/initial_prompt_{x}'
            )
            for x in ['a', 'b'])

        return prompt_a, prompt_b

    def create_prompt(self, prompt: str, word: str, n_turns: int) -> str:
        text = string.Template(prompt).substitute(
                t_word=word,
                nturns=n_turns)
        return text

    def generate(self, filename="in/instances.json", **kwargs):
        self.on_generate(**kwargs)
        with open(filename, 'w', encoding='utf-8') as json_file:
            json.dump(self.instances, json_file, indent=4, ensure_ascii=False)

    def pick_starting_word(self, difficulty):
        base_path = os.getcwd()
        # FIXME: For this you have to be in the game's folder
        with open(f"{base_path}/resources/words/word_pool.json", 'r') as file:
            word_pool = json.load(file)

        # Define syllable counts based on difficulty level
        if difficulty == "EASY":
            syllables = 2
        elif difficulty == "MEDIUM":
            syllables = 2  # FIXME: Adjust
        elif difficulty == "CO-OP":
            syllables = 2  # FIXME: Adjust
        else:
            raise ValueError(f"Unknown difficulty level: {difficulty}")

        picked_word = random.choice([entry['word'] for entry in word_pool
                                     if entry['num_syllables'] == syllables])
        return picked_word


if __name__ == '__main__':
    SoundAlikeInstanceGenerator().generate()
