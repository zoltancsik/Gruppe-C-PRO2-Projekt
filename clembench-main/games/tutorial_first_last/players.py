import random
from string import ascii_lowercase as letters
from typing import List
from clemgame.clemgame import Player


class Speaker(Player):
    def __init__(self, model_name: str, player: str, letter: str):
        super().__init__(model_name)
        self.player: str = player
        self.initial_letter: str = letter
        self.history: List = []

    def _custom_response(self, messages, turn_idx) -> str:
        """Return a mock message with the suitable letter and format."""
        if turn_idx == 1 and self.player == 'A':
            letter = 'I SAY: ' + self.initial_letter
        else:
            previous_letter = messages[-1]['content'][7].lower()
            # introduce a small probability that the player fails
            letter = self._sample_letter(previous_letter)
        # return a string whose first and last tokens start with the next letter     
        return f"{letter}xxx from {self.player}, turn {turn_idx} {letter.replace('I SAY: ', '')}xxx."

    # an additional method specific for this game
    # for testing, we want the utterances to be invalid or incorrect sometimes
    def _sample_letter(self, letter: str) -> str:
        """Randomly decide which letter to use in the message."""
        prob = random.random() 
        index = letters.index(letter)
        if prob < 0.05:
            # correct but invalid (no tag)
            return letters[index + 1]
        if prob < 0.1:
            # valid tag but wrong letter
            return 'I SAY: ' + letter
        # valid and correct
        return 'I SAY: ' + letters[index + 1]
