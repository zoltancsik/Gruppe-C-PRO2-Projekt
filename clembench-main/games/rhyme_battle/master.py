import re
import copy
import json
from typing import List, Dict
from clemgame.clemgame import (DialogueGameMaster,
                               GameBenchmark,
                               GameScorer,
                               GameMaster)
from games.rhyme_battle.players import Guesser

GAME_NAME = "rhyme_battle"
WILD_CARDS = ["Appreciation", "Inauguration", "Consideration"]


class RhymeBattleGameMaster(DialogueGameMaster):
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
        self.trick_attempt = 0

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
        # MOVE_RULE VIOLATED
        if not self._parse_and_validate(answer_a, 'a'):
            self._update_history(f"{answer_a} was invalid", 'b', 'user')

        else:
            # Logging A's answer to B's History
            self.distribute_points('a', 0.5)

            self._update_history(answer_a, 'b', 'user')
            action = {'type': 'send message', 'content': answer_a}
            self.log_event(from_='GM', to='Player 2', action=action)

        answer_b = self._get_answer('b')
        # MOVE RULE VIOLATED
        if not self._parse_and_validate(answer_b, 'b'):
            self._update_history(f"{answer_b} was invalid", 'a', 'user')

        else:
            # Logging B's answer to A's History
            self.distribute_points('b', 0.5)

            self._update_history(answer_b, 'a', 'user')
            action = {'type': 'send message', 'content': answer_b}
            self.log_event(from_='GM', to='Player 1', action=action)

        turn_end_info = (f"Round: {self.current_turn}"
                         f" | Words so far: {self.words_list}"
                         f" | Points Player A: {self.player_a.points}"
                         f" | Points Player B: {self.player_b.points}")
        self._update_history(turn_end_info, 'a', "system")
        self._update_history(turn_end_info, 'b', "system")

        self.current_turn += 1

    def _get_answer(self, player):
        assert player in ('a', 'b')
        if player == 'a':
            # The Player's History is turned into a prompt
            # With the Player classes __call__ method.
            # self.player_a.history.append(f"Words so far {self.words_list}")
            prompt, raw_answer, answer = self.player_a(self.player_a.history, self.n_turns)
            action = {'type': 'get message', 'content': answer}
            self.log_event(from_='Player A', to='GM', action=action,
                           call=(copy.deepcopy(prompt), raw_answer))
            self._update_history(answer, 'a', 'assistant')

            # FIXME: Build Interface for readability
            print("\n")
            print(f"===[ TURN: {self.current_turn}/{self.n_turns} |"
                  f" LVL: {self.difficulty} | "
                  f"POINTS: A:{self.player_a.points}|B:{self.player_b.points}"
                  f"/{self.points_needed}]===")
            print(f"A - {self.player_a.model}: {answer}")

        else:
            prompt, raw_answer, answer = self.player_b(self.player_b.history, self.n_turns)
            action = {'type': 'get message', 'content': answer}
            self.log_event(from_='Player B', to='GM', action=action,
                           call=(copy.deepcopy(prompt), raw_answer))
            self._update_history(answer, 'b', 'assistant')
            print(f"B - {self.player_b.model}: {answer}")

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
        match = re.search(r'MY GUESS: (\w+)', answer)
        if match:
            word = match.group(1)
            if isinstance(word, str):
                if word not in self.words_list:
                    if word in WILD_CARDS:
                        self.trick_attempt = 1
                        # self._update_history("Trying to trick the other Player", 'a', 'system')
                    elif word == "JINX" and self.trick_attempt == 1:
                        self.trick_attempt = 0
                        print("Player A tried to cheat!!!")
                        # self._update_history("You detected the other player's cheating move", 'b', 'system')
                    elif word not in WILD_CARDS and word != "JINX":
                        self.words_list.append(word)
                    return True
                else:
                    print(f"Player {player}: {word} was already used, you lost a point")
                    return False
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
        else:
            self.player_b.points += points

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


class RhymeBattleGameBenchmark(GameBenchmark):
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
        return RhymeBattleGameMaster(experiment, players)


class RhymeBattleGameScorer(GameScorer):
    def __init__():
        pass
