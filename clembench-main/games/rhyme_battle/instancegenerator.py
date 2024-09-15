import json
import random
import string
import os
from clemgame.clemgame import GameInstanceGenerator

LEVELS = ['EASY', 'HARD', 'CO-OP']
GAME_NAME = 'rhyme_battle'
N_INSTANCES = 4
N_EPISODES = 3
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
                n_turns = random.choice([10, 20])
                max_p = 12
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
                f"{script_dir}/resources/initial_prompts/"
                f"{folder}/initial_prompt_{x}"
            )
            for x in ['a', 'b'])

        return prompt_a, prompt_b

    def create_prompt(self, prompt: str,
                      word: str, n_turns: int,
                      max_p: int,
                      wild_cards: list) -> str:

        text = string.Template(prompt).substitute(
                t_word=word, nturns=n_turns,
                max_p=max_p, wild_cards=wild_cards)
        return text

    def generate(self, filename=f"{script_dir}/in/instances.json", **kwargs):
        self.on_generate(**kwargs)
        with open(filename, 'w', encoding='utf-8') as json_file:
            json.dump(self.instances, json_file, indent=4, ensure_ascii=False)

    def pick_starting_word(self, difficulty):
        with open(
            f"{script_dir}/resources/starting_words/"
                f"starting_words_pool.json", 'r') as file:
            word_pool = json.load(file)

        if difficulty == "EASY":
            syllables = 2
        elif difficulty == "HARD":
            syllables = 3
        elif difficulty == "CO-OP":
            syllables = 4
        else:
            raise ValueError(f"Unknown difficulty level: {difficulty}")

        picked_word = random.choice([entry['word'] for entry in word_pool
                                     if entry['num_syllables'] == syllables])
        return picked_word


class PromptGenerator():
    def __init__(self):
        self.prompts_created = 0

    def generate_prompt(self, difficulty, prompt_message, player):
        if difficulty == "EASY":
            folder = "level_easy"
        elif difficulty == "HARD":
            folder = "level_hard"
        elif difficulty == "CO-OP":
            folder = "level_coop"
        if player == 'a':
            x = 'a'
        else:
            x = 'b'
        with open(
                f'resources/initial_prompts/{folder}/'
                f'initial_prompt_{x}.template', 'w') as file:
            file.write(prompt_message)
        self.prompts_created += 1

    def generator_infos(self):
        return print(f"PROMPTS: {self.prompts_created} Initial Prompts have been created")


if __name__ == '__main__':
    prompt_easy_a = (
        "Your task come up with a  word that likely rhymes with '$t_word', using phonetic rules. "
        "Two words rhyme if they share the same vowel in the last stressed syllable and all following sounds. "
        "Try to Provide a perfect rhyming word (exact match after the stressed vowel) or a near rhyming word (minor variations allowed)."
        "Use phonetic transcriptions similar to those in linguistic dictionaries like CMUdict."
        "Your have to reach $max_p points before the other player. "
        "Your answer must follow this format: [Previous Word] -  MY GUESS: word. "
        "Your answer can not contain special characters or any other information."
        "Each round, you consider your partner's current points, "
        "Your secondary objective is to trick the other player as often as possible "
        "by using one of the following words: $wild_cards."
        "If you use a wildcard word and the other player catches you, you will be penalized."
        "Try not to use words that have been used before")

    prompt_easy_b = (
        "Your task is to find a word that rhymes with the word the other player said, using phonetic rules. "
        "Two words rhyme if they share the same vowel in the last stressed syllable and all following sounds. "
        "Try toProvide a perfect rhyming word (exact match after the stressed vowel) or a near rhyming word (minor variations allowed)."
        "Use phonetic transcriptions similar to those in linguistic dictionaries like CMUdict."
        "Your have to reach $max_p points before the other player. "
        "Your answer must follow this format: [Previous Word] -   MY GUESS: word. "
        "Your answer can not contain special characters or any other information."
        "if you think the other player is trying to trick you "
        "by using a word that is phonetically completely different than the last word, "
        "call them out by answering: MY GUESS: CHEATER."
        "Try not to use words that have been used before"
    )

    prompt_hard_a = (
        "Your task is to come up with a sentence that rhymes with $t_word. "
        "Review your previous turns and the points you've received for the last words in your sentences. "
        "Look for patterns in the phonetic properties to improve your guesses."
        "If you recieve 0.5 points, that means your guess is barely acceptable and you need to rhyme better. "
        "Your have to reach $max_p points before the other player. "
        "Your answer can only consist of your sentence "
        "Your answer can not contain special characters."
        "Do not use words at the end of your sentence that have been used before"
    )

    prompt_hard_b = (
        "Your task is to come up with a sentence that rhymes with the last word in other player's sentence "
        "Review your previous turns and the points you've received for the last words in your sentences. "
        "Look for patterns in the phonetic properties to improve your guesses."
        "If you recieve 0.5 points, that means your guess is barely acceptable and you need to rhyme better. "
        "Your have to reach $max_p points before the other player. "
        "Your answer can only consist of your sentence "
        "Your answer can not contain special characters."
        "Do not use words at the end of your sentence that have been used before"
    )

    prompt_co_op = (
        "Your task is to build a word chain where each word rhymes with $t_word. "
        "Review your previous turns and the points you've received for the last words in your sentences. "
        "Look for patterns in the phonetic properties to improve your guesses."
        "If you recieve 0.5 points, that means your guess is barely acceptable and you need to rhyme better. "
        "Your have to reach $max_p points together with your partner. "
        "Your answer can only consist of the word you'd like to add to the chain "
        "Your answer can not contain special characters."
        "Do not use words that have been used before"
    )

    prompt_generator = PromptGenerator()
    prompt_generator.generate_prompt("EASY", prompt_easy_a, 'a')
    prompt_generator.generate_prompt("EASY", prompt_easy_b, 'b')
    prompt_generator.generate_prompt("HARD", prompt_hard_a, 'a')
    prompt_generator.generate_prompt("HARD", prompt_hard_b, 'b')
    prompt_generator.generate_prompt("CO-OP", prompt_co_op, 'a')
    prompt_generator.generate_prompt("CO-OP", prompt_co_op, 'b')
    prompt_generator.generator_infos()
    created_episodes = RhymeBattleInstanceGenerator()
    created_episodes.generate()
    print(f"INSTANCES: Created Experiment with {N_EPISODES} Episodes and "
          f"{N_EPISODES*N_INSTANCES} Instances")
