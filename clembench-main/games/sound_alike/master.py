from typing import List, Dict
from clemgame.clemgame import (DialogueGameMaster,
                               GameBenchmark,
                               GameScorer,
                               GameMaster)
from games.sound_alike.players import Guesser

GAME_NAME = "sound_alike"


class SoundAlikeGameMaster(DialogueGameMaster):
    def __init__(self, experiment: Dict, players: List[str]):
        super().__init__(GAME_NAME, experiment, players)

        # Players = Models
        self.model_a = players[0]
        self.model_b = players[1]

    def setup(self, prompt_player_a, prompt_player_b, n_turns, game_id):
        # Setting up Players and Prompts
        self.player_a = Guesser(self.model_a, 'Player A')
        self.player_b = Guesser(self.model_b, 'Player B')
        self.prompt_a = prompt_player_a
        self.prompt_b = prompt_player_b

        # Game Metrics
        self.n_turns = n_turns
        self.current_turn = 0
        self.starting_word = self._pick_first_word()
        self.current_word = None

        # Common Metrics
        self.request_counts = [0] * (n_turns + 1)
        self.parsed_request_counts = [0] * (n_turns + 1)
        self.violated_request_counts = [0] * (n_turns + 1)

        # Logging
        self.log_players({
            'GM': 'SoundAlike GM',
            'Player 1': f'Player A: {self.model_a}',
            'Player 2': f'Player B: {self.model_b}'
            })
        self.log_key('n_turns', n_turns)
        self.log_key('starting_word', self.starting_word)
        self.log_key('current_word', self.current_word)
        self.log_next_turn()

        # Appending prompts to player.history
        self.player_a.history.append(
            {'role': 'user', 'content': prompt_player_a})
        self.player_b.history.append(
            {'role': 'user', 'content': prompt_player_b})
        action = {'type': 'send message', 'content': prompt_player_a}
        self.log_event(from_='GM', to='Player 1', action=action)
        action = {'type': 'send message', 'content': prompt_player_b}
        self.log_event(from_='GM', to='Player 2', action=action)

    def _pick_first_word(self):
        word_pool = self.load_file("resources/word_pool", ".txt")
        return word_pool


class SoundAlikeGameBenchmark(GameBenchmark):
    def __init__(self):
        super().__init__(GAME_NAME)

    def is_single_player(self):
        return False

    def get_description(self):
        # This shows up when scripts/cli.py ls
        return ("Players must find phonetically similar words, "
                "that have different meanings.")

    def create_game_master(self,
                           experiment: Dict,
                           players: List[str]
                           ) -> GameMaster:
        return SoundAlikeGameMaster(experiment, players)


class SoundAlikeGameScorer(GameScorer):
    def __init__():
        pass


# def main():
#     """ FIRST STEP """
#     bm = SoundAlikeGameBenchmark()
#     bm.setup()  # Read in Experiments
#     experiments = bm.instances
#     gm = bm.create_game_master(bm.instances, ['A', 'B'])

#     """SECOND STEP"""
#     prompt_a = experiments["experiments"][0]
#     ["game_instances"][0]["prompt_player_a"]
#     prompt_b = experiments["experiments"][0]
#     ["game_instances"][0]["prompt_player_b"]
#     gm.setup(prompt_a, prompt_b)
#     print(gm.prompt_a)
#     print(gm.prompt_b)
#     print(gm.first_word)


# if __name__ == "__main__":
#     main()
