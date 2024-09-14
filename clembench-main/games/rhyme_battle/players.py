from typing import List
from clemgame.clemgame import Player


class Guesser(Player):
    def __init__(self, model_name: str, name: str, points: int):
        super().__init__(model_name)
        self.name: str = name
        self.history: List = []
        self.answer: str = ""
        self.model = model_name
        self.points = points

    def _custom_response(self) -> str:
        return "MY Gdsa Wort"

    def __str__(self) -> str:
        return f"{self.model}"
