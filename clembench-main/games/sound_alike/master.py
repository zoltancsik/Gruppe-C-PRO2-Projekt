import copy
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

        # Attributes for Evaluation
        self.aborted: bool = False
        self.lose: bool = False
        self.complete_turns: int = 0

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

    def play(self) -> None:
        while self.continue_round():
            # Main Loop
            self.complete_turns += 1
            self.log_next_turn()
            self.conduct_turn()

        if self.complete_turns == self.n_turns:
            action = {'type': 'info', 'content': 'game successful'}
            self.log_event(from_='GM', to='GM', action=action)

        action = {'type': 'info', 'content': 'end game'}
        self.log_event(from_='GM', to='GM', action=action)
        # self.log_eval_assets()

    def conduct_turn(self):
        answer_a = self._get_answer('a')
        answer_b = self._get_answer('b')

        if not self._validate_answer(answer_a):
            return None

        if not self._validate_answer(answer_b):
            return None

        # Logging and History Updates
        self._add_answer(answer_a, 'b', 'user')
        action = {'type': 'send message', 'content': answer_a}
        self.log_event(from_='GM', to='Player 2', action=action)
        self._add_answer(answer_b, 'a', 'user')
        action = {'type': 'send message', 'content': answer_b}
        self.log_event(from_='GM', to='Player 1', action=action)

        self.current_turn += 1

    def _get_answer(self, player):
        assert player in ('a', 'b')
        if player == 'a':
            prompt, raw_answer, answer = self.player_a(self.player_a.history,
                                                       self.current_turn)
            action = {'type': 'get message', 'content': answer}
            self.log_event(from_='Player 1', to='GM', action=action,
                           call=(copy.deepcopy(prompt), raw_answer))
            self._add_answer(answer, 'a', 'assistant')
            print(f"Turn {self.current_turn} | Player A:")
            print(answer)

        else:
            prompt, raw_answer, answer = self.player_b(self.player_b.history,
                                                       self.current_turn)
            action = {'type': 'get message', 'content': answer}
            self.log_event(from_='Player 2', to='GM', action=action,
                           call=(copy.deepcopy(prompt), raw_answer))
            self._add_answer(answer, 'b', 'assistant')
            print(f"Turn {self.current_turn} | Player B:")
            print(answer)

        self.request_counts[self.current_turn] += 1
        return answer

    def _add_answer(self, utterance, player, role):
        assert player in ('a', 'b')
        if player == 'a':
            self.player_a.history.append({'role': role, 'content': utterance})
        else:
            self.player_b.history.append({'role': role, 'content': utterance})

    def _validate_answer(self, answer):
        # FIXME: Needs to be Implemented
        if isinstance(answer, str):
            return True
        else:
            return False

    def continue_round(self):
        # FIXME: Needs to be Implemented
        if self.complete_turns < self.n_turns:
            return True
        else:
            return False

    def _pick_first_word(self):
        # FIXME: Needs to be implemented
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
