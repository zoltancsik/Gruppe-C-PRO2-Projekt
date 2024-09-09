from typing import List, Dict
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

        # Evaluation Scores
        self.aborted: bool = False
        self.lose: bool = False
        self.complete_turns: int = 0

    def setup(self, current_word: str, n_turns: int, prompt_player_a: str,
              prompt_player_b: str) -> None:

        # Players
        self.player_a = Player(self.model_a, 'A')
        self.player_b = Player(self.model_b, 'B')

        # Game Variables
        self.n_turns = n_turns
        self.current_turn: int = 0
        self.current_word: str = current_word

        # Common Metrics
        self.request_counts = [0] * (n_turns + 1)
        self.parsed_request_counts = [0] * (n_turns + 1)
        self.violated_request_counts = [0] * (n_turns + 1)

        # Initiate first turn
        self.initiate(prompt_player_a, prompt_player_b)

        self.log_players({
            'GM': 'SoundAlike GameMaster',
            'Player 1': f'Player A: {self.model_a}',
            'Player 2': f'Player B: {self.model_b}'
            })

        self.log_key('n_turns', n_turns)

    def initiate(self, prompt_player_a: str, prompt_player_b: str) -> None:
        self.log_next_turn()
        # Player history (List)
        self.player_a.history.append(
            {'role': 'user', 'content': prompt_player_a})
        self.player_b.history.append(
            {'role': 'user', 'content': prompt_player_b})

        action = {'type': 'send message', 'content': prompt_player_a}
        self.log_event(from_='GM', to='Player 1', action=action)
        action = {'type': 'send message', 'content': prompt_player_b}
        self.log_event(from_='GM', to='Player 2', action=action)

    def play(self) -> None:
        while self.should_continue():
            self.current_turn += 1
            self.log_next_turn()
            self.turn()

        if self.complete_turns == self.n_turns:
            action = {'type': 'info', 'content': 'game successful'}
            self.log_event(from_='GM', to='GM', action=action)

        action = {'type': 'info', 'content': 'end game'}
        self.log_event(from_='GM', to='GM', action=action)
        self.log_eval_assets()

    def should_continue(self) -> None:
        return (self.current_turn < self.n_turns
                and not self.aborted
                and not self.lose)

    def process_answer(self):
        pass

    def is_correct_answer(self):
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
