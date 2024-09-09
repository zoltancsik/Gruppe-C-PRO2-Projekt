import copy
from typing import List, Dict, Tuple
from clemgame.clemgame import (DialogueGameMaster,
                               GameBenchmark,
                               GameScorer,
                               GameMaster,
                               Player)

GAME_NAME = "SoundAlike"


class SoundAlikeGameMaster(DialogueGameMaster):
    def __init__(self, experiment: Dict, player_backends: List[str]):
        super().__init__(GAME_NAME, experiment, player_backends)

        # Players = Models
        self.model_a = player_backends[0]
        self.model_b = player_backends[1]

    def setup(self, base_word, prompt_a, prompt_b, game_id):
        print(prompt_a)
        print(prompt_b)
        print(game_id)
        print(base_word)


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


class SoundAlikeGameScorer(GameScorer):
    def __init__():
        pass
