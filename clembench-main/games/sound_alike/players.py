from typing import List
from clemgame.clemgame import Player


class Speaker(Player):
    def __init__(self, model_name: str, player: str):
        super().__init__(model_name)
        self.player: str = player
        self.history: List = []
