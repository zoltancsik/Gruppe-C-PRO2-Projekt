import json
import random
import string
from clemgame.clemgame import GameInstanceGenerator

LEVELS = ['EASY', 'HARD', 'CO-OP']
GAME_NAME = 'sound_alike'
N_INSTANCES = 3
N_EPISODES = 1


class SoundAlikeInstanceGenerator(GameInstanceGenerator):
    def __init__(self):
        super().__init__(GAME_NAME)

    def on_generate(self):
        prompt_a, prompt_b = (
            self.load_template(f'resources/initial_prompts/initial_prompt_{x}')
            for x in ['a', 'b']
        )

        for episode in range(N_EPISODES):
            experiment = self.add_experiment(f"Episode {episode}")
            for game_id in range(N_INSTANCES):
                instance = self.add_game_instance(experiment, game_id)
                difficulity = random.choice(LEVELS)
                first_word = self.pick_starting_word(difficulity)
                instance['difficulity'] = difficulity
                n_turns = 3
                instance['n_turns'] = n_turns
                instance['starting_word'] = first_word
                instance['prompt_player_a'] = self.create_prompt(
                    prompt_a, first_word,  n_turns)
                instance['prompt_player_b'] = self.create_prompt(
                    prompt_b, first_word,  n_turns)
                print(f"Game ID: {game_id}, DIFF: {difficulity}, WORD: {first_word}")

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
        with open("resources/words/word_pool.json", 'r') as file:
            word_pool = json.load(file)

        # Define syllable counts based on difficulty level
        if difficulty == "EASY":
            syllables = 2
        elif difficulty == "HARD":
            syllables = 2
        elif difficulty == "CO-OP":
            syllables = 2
        else:
            raise ValueError(f"Unknown difficulty level: {difficulty}")

        picked_word = random.choice([entry['word'] for entry in word_pool
                                     if entry['num_syllables'] == syllables])
        return picked_word


if __name__ == '__main__':
    SoundAlikeInstanceGenerator().generate()
