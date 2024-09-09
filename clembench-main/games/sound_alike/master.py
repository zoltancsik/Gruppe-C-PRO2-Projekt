from typing import List, Dict
from clemgame.clemgame import (DialogueGameMaster,
                               GameBenchmark,
                               GameScorer,
                               GameMaster)

GAME_NAME = "SoundAlike"


class SoundAlikeGameMaster(DialogueGameMaster):
    def __init__(self, experiment: Dict, player_backends: List[str]):
        super().__init__(GAME_NAME, experiment, player_backends)

        # Players
        self.model_a = player_backends[0]
        self.model_b = player_backends[1]

        # Evaluation Scores
        self.aborted: bool = False
        self.lose: bool = False
        self.complete_turns: int = 0

    def pick_starting_word(self, words_list):
        pass


class SoundAlikeGameScorer(GameScorer):
    def __init__():
        pass


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
                           player_backends: List[str]
                           ) -> GameMaster:
        return SoundAlikeGameMaster(experiment, player_backends)
