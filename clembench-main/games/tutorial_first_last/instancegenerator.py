import random
import string
from clemgame.clemgame import GameInstanceGenerator

GAME_NAME = 'tutorial_first_last'
N_INSTANCES = 10
SEED = 123


class TutorialFirstLastGameInstanceGenerator(GameInstanceGenerator):
    def __init__(self):
        super().__init__(GAME_NAME)

    def on_generate(self):
        topics = self.load_file('resources/topics.txt').strip('\n').split('\n')
        prompt_a = self.load_template('resources/initial_prompts/initial_prompt_a')
        prompt_b = self.load_template('resources/initial_prompts/initial_prompt_b')

        for topic in topics:
            experiment = self.add_experiment(topic)
            for game_id in range(N_INSTANCES):
                letter = random.choice(string.ascii_lowercase[:5])
                n_turns = random.randint(3, 8)
                instance = self.add_game_instance(experiment, game_id)
                instance['first_letter'] = letter
                instance['n_turns'] = n_turns
                instance['prompt_player_a'] = self.create_prompt(
                    topic, prompt_a, letter, n_turns)
                instance['prompt_player_b'] = self.create_prompt(
                    topic, prompt_b, letter, n_turns)

    def create_prompt(self,
                      topic: str,
                      prompt: str,
                      letter: str,
                      n_turns: int) -> str:
        """Replace a prompt template with slot values."""
        text = string.Template(prompt).substitute(topic=topic, letter=letter,
                                                  nturns=n_turns)
        return text


if __name__ == '__main__':
    random.seed(SEED)
    TutorialFirstLastGameInstanceGenerator().generate()
