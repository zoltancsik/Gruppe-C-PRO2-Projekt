import re
import copy
import json
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
        self.words_list = []

    def setup(self, init_prompt_a, init_prompt_b,
              n_turns, difficulty, game_id, starting_word,
              points_needed):
        # Setting up Players and Prompts
        self.player_a = Guesser(self.model_a, 'Player A', 0)
        self.player_b = Guesser(self.model_b, 'Player B', 0)
        self.init_prompt_a = init_prompt_a
        self.init_prompt_b = init_prompt_b
        self.difficulty = difficulty
        self.words_list.append(starting_word)
        self.points_needed = points_needed
        self.points = 0

        # Game Metrics
        self.n_turns = n_turns
        self.starting_word = starting_word
        self.current_word = None
        self.game_id = game_id
        self.current_turn = 0

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
            {'role': 'system', 'content': self.init_prompt_a})
        self.player_b.history.append(
            {'role': 'system', 'content': self.init_prompt_b})
        action = {'type': 'send message', 'content': self.init_prompt_a}
        self.log_event(from_='GM', to='Player 1', action=action)
        action = {'type': 'send message', 'content': self.init_prompt_b}
        self.log_event(from_='GM', to='Player 2', action=action)

    def play(self) -> None:
        while self.continue_round():
            # Main Loop
            self.complete_turns += 1
            self.log_next_turn()
            self.conduct_turn()

        if self.points >= self.points_needed:
            action = {'type': 'info', 'content': 'game successful'}
            self.log_event(from_='GM', to='GM', action=action)

        action = {'type': 'info', 'content': 'end game'}
        self.log_event(from_='GM', to='GM', action=action)
        self.log_eval_assets()

    def conduct_turn(self):
        # PLAYER A
        answer_a = self._get_answer('a')
        if not self._parse_and_validate(answer_a, 'a'):
            return None

        # Logging A's answer to B's History
        self.distribute_points('a', 1)
        self._update_history(answer_a, 'b', 'user')
        action = {'type': 'send message', 'content': answer_a}
        self.log_event(from_='GM', to='Player 2', action=action)

        answer_b = self._get_answer('b')
        if not self._parse_and_validate(answer_b, 'b'):
            return None

        # Logging B's answer to A's History
        self.distribute_points('b', 1)
        self._update_history(answer_b, 'a', 'user')
        action = {'type': 'send message', 'content': answer_b}
        self.log_event(from_='GM', to='Player 1', action=action)

        self.current_turn += 1

    def _get_answer(self, player):
        assert player in ('a', 'b')
        if player == 'a':
            # The Player's History is passed as an arg before every turn
            prompt, raw_answer, answer = self.player_a(self.player_a.history,
                                                       self.n_turns)
            action = {'type': 'get message', 'content': answer}
            self.log_event(from_='Player A', to='GM', action=action,
                           call=(copy.deepcopy(prompt), raw_answer))
            self._update_history(answer, 'a', 'assistant')

            # FIXME: Build Interface for readability
            print("\n")
            print(f"===[ TURN: {self.current_turn}/{self.n_turns} |"
                  f" LVL: {self.difficulty} | "
                  f"POINTS: {self.player_a.points}/{self.player_b.points} ]==="
                  f"POINTS NEEDED: {self.points_needed}")
            print(f"A - {self.player_a.model}: {answer}")

        else:
            prompt, raw_answer, answer = self.player_b(self.player_b.history,
                                                       self.n_turns)
            action = {'type': 'get message', 'content': answer}
            self.log_event(from_='Player B', to='GM', action=action,
                           call=(copy.deepcopy(prompt), raw_answer))
            self._update_history(answer, 'b', 'assistant')
            print(f"B - {self.player_b.model}: {answer}")

        # self.request_counts[self.current_turn] += 1
        return answer

    def _update_history(self, info, player, role):
        assert player in ('a', 'b')
        if player == 'a':
            self.player_a.history.append({'role': role, 'content': info})
            with open('history_player_a.json', 'w', encoding='utf-8') as fle:
                json.dump(self.player_a.history, fle, indent=4, ensure_ascii=False)
        else:
            self.player_b.history.append({'role': role, 'content': info})
            with open('history_player_b.json', 'w', encoding='utf-8') as fle:
                json.dump(self.player_b.history, fle, indent=4, ensure_ascii=False)

    def _parse_and_validate(self, answer, player):
        # MOVE_RULE
        match = re.search(r'similar to (\w+)\.', answer)
        if match:
            word = match.group(1)
            if isinstance(word, str):
                if match not in self.words_list:
                    self.words_list.append(word)
                    return True
                else:
                    print(f"{word} was already used, you lost a point")
        else:
            print("MOVE_RULE Violated")
            return False

    def get_points(self, player):
        if player == 'a':
            return self.player_a.points
        else:
            return self.player_b.points

    def distribute_points(self, player, points):
        if player == 'a':
            self.player_a.points += points
            # # Add A's point to B's history
            # point_msg = (f"Other player {'gained' if points > 0 else 'lost'}"
            #              f" {abs(points)} point. "
            #              f"And has {self.player_a.points} points so far")
            # self._update_history(point_msg, 'b', "system")
        else:
            self.player_b.points += points
            # # Add B's point to A's history
            # point_msg = (f"Other player {'gained' if points > 0 else 'lost'}"
            #              f" {abs(points)} point. "
            #              f"And has {self.player_b.points} points so far")
            # self._update_history(point_msg, 'a', "system")

    def continue_round(self):
        points_a = self.player_a.points
        points_b = self.player_b.points
        if (points_a or points_b) < self.points_needed:
            return True
        else:
            print("====================[GAME OVER]====================")
            print(f"POINTS: A:{points_a} B: {points_b}/{self.points_needed} "
                  f"ROUNDS: {self.current_turn}/{self.n_turns}")

    def log_eval_assets(self) -> None:
        self.log_key('Played turns', self.current_turn)
        self.log_key('Complete turns', self.complete_turns)
        self.log_key('Points Collected', self.points)
        self.log_key('Points Needed', self.points_needed)


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
