import json
import random
import string
import os
from clemgame.clemgame import GameInstanceGenerator

LEVELS = ['EASY']
GAME_NAME = 'rhyme_battle'
N_INSTANCES = 1
N_EPISODES = 1
WILD_CARDS = ["Appreciation", "Inauguration", "Consideration"]
script_dir = os.path.dirname(os.path.abspath(__file__))


class RhymeBattleInstanceGenerator(GameInstanceGenerator):
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
                n_turns = random.choice([5, 10])
                max_p = 5  # FIXME: Adjust to each difficulty

                prompt_a, prompt_b = self._load_custom_prompts(difficulty)
                instance = self.add_game_instance(experiment, game_id)
                instance['difficulty'] = difficulty
                instance['n_turns'] = n_turns
                instance['starting_word'] = first_word
                instance['points_needed'] = max_p
                instance['init_prompt_a'] = self.create_prompt(
                    prompt_a, first_word,  n_turns, max_p, WILD_CARDS)
                instance['init_prompt_b'] = self.create_prompt(
                    prompt_b, first_word,  n_turns, max_p, WILD_CARDS)

    def _load_custom_prompts(self, difficulty):
        if difficulty == "EASY":
            folder = "level_easy"
        elif difficulty == "HARD":
            folder = "level_hard"
        elif difficulty == "CO-OP":
            folder = "level_coop"
        prompt_a, prompt_b = (
            self.load_template
            (
                f'{script_dir}/resources/initial_prompts/{folder}/initial_prompt_{x}'
            )
            for x in ['a', 'b'])

        return prompt_a, prompt_b

    def create_prompt(self, prompt: str,
                      word: str, n_turns: int,
                      max_p: int,
                      wild_cards: list) -> str:
        text = string.Template(prompt).substitute(
                t_word=word,
                nturns=n_turns,
                max_p=max_p,
                wild_cards=wild_cards)
        return text

    def generate(self, filename=f"{script_dir}/in/instances.json", **kwargs):
        self.on_generate(**kwargs)
        with open(filename, 'w', encoding='utf-8') as json_file:
            json.dump(self.instances, json_file, indent=4, ensure_ascii=False)

    def pick_starting_word(self, difficulty):
        with open(f"{script_dir}/resources/words/word_pool.json", 'r') as file:
            word_pool = json.load(file)

        # Define syllable counts based on difficulty level
        if difficulty == "EASY":
            syllables = 2
        elif difficulty == "HARD":
            syllables = 2  # FIXME: Adjust
        elif difficulty == "CO-OP":
            syllables = 2  # FIXME: Adjust
        else:
            raise ValueError(f"Unknown difficulty level: {difficulty}")

        picked_word = random.choice([entry['word'] for entry in word_pool
                                     if entry['num_syllables'] == syllables])
        return picked_word


if __name__ == '__main__':
    created_episodes = RhymeBattleInstanceGenerator()
    created_episodes.generate()
    print(f"Finished Creating Experiment with {N_EPISODES} Episodes and "
          f"{N_EPISODES*N_INSTANCES} Instances")
