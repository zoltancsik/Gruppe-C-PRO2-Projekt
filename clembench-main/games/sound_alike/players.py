from typing import List
from clemgame.clemgame import Player


class Guesser(Player):
    def __init__(self, model_name: str, player: str):
        super().__init__(model_name)
        self.player: str = player
        self.history: List = []
        self.answer: str = ""
        self.model = model_name

    def _custom_response(self, messages) -> str:
        last_message = messages[-1]["content"]
        return f"My answer to {last_message} is X"

    def __str__(self) -> str:
        return f"{self.model}"
