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
        self.history_list = []

    def setup(self, init_prompt_a, init_prompt_b,
              n_turns, difficulty, game_id, starting_word,
              points_needed):
        # Setting up Players and Prompts
        self.player_a = Guesser(self.model_a, 'Player A', 0)
        self.player_b = Guesser(self.model_b, 'Player B', 0)
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
        self._update_history(init_prompt_a, self.player_a, 'system')
        self._update_history(init_prompt_b, self.player_b, 'system')

        action = {'type': 'send message', 'content': init_prompt_a}
        self.log_event(from_='GM', to='Player 1', action=action)
        action = {'type': 'send message', 'content': init_prompt_b}
        self.log_event(from_='GM', to='Player 2', action=action)

    def play(self) -> None:
        while self.turn():
            if self.player_a.points >= self.points_needed or \
               self.player_b.points >= self.points_needed:
                print("Player A Won")
                break
            elif self.current_turn >= self.n_turns:
                print("Maximum Turn Count reached")
                break

        print("====================[GAME OVER]====================")
        print(f"POINTS: A:{self.player_a.points} B: "
              f"{self.player_b.points}/{self.points_needed} "
              f"ROUNDS: {self.current_turn}/{self.n_turns}")
        action = {'type': 'info', 'content': 'end game'}
        self.log_event(from_='GM', to='GM', action=action)
        self.log_eval_assets()

    def turn(self):
        # PLAYER A
        answer_a = self._get_answer('a')
        if not self._parse_answer(answer_a, self.player_a):
            pass
        else:
            self.distribute_points('a', 0.5)
            self._update_history(answer_a, self.player_a, 'assistant')
            self._update_history(answer_a, self.player_b, 'user')
            action = {'type': 'send message', 'content': answer_a}
            self.log_event(from_='GM', to='Player 2', action=action)

        # PLAYER B
        answer_b = self._get_answer('b')
        if not self._parse_answer(answer_b, self.player_b):
            pass
        else:
            self.distribute_points('b', 0.5)
            self._update_history(answer_b, self.player_b, 'assistant')
            self._update_history(answer_b, self.player_a, 'user')
            action = {'type': 'send message', 'content': answer_b}
            self.log_event(from_='GM', to='Player 1', action=action)

        self.current_turn += 1
        self.log_next_turn()
        return True

    def _get_answer(self, player):
        assert player in ('a', 'b')
        if player == 'a':
            prompt, raw_answer, answer = self.player_a(self.player_a.history, self.n_turns)
            action = {'type': 'get message', 'content': answer}

            self.log_event(from_='Player A', to='GM', action=action,
                           call=(copy.deepcopy(prompt), raw_answer))

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
            print(f"B - {self.player_b.model}: {answer}")

        return answer

    def _update_history(self, info, player_obj, role):
        player_obj.history.append(
            {
                'player': player_obj.name,
                'role': role,
                'content': info,
                'turn': self.current_turn,
                'points': player_obj.points,
                'words_so_far': self.words_list
            })

        with open(f'history_{player_obj.name}.json', 'w', encoding='utf-8') as fle:
            json.dump(player_obj.history, fle, indent=4, ensure_ascii=False)

    def _parse_answer(self, answer, player):
        # MOVE_RULE: Answer has to include MY GUESS: word
        match = re.search(r'MY GUESS: (\w+)', answer)
        if match:
            word = match.group(1)
            if self._validate_answer(word, player):
                return True
            else:
                print("GAME_RULE violated, skipping turn")
                return False
        else:
            msg = "Incorrect. Answer has to be in the format MY GUESS: word"
            if player.name == 'Player A':
                self._update_history(msg, self.player_a, 'assistant')
                self._update_history(msg, self.player_b, 'user')
            else:
                self._update_history(msg, self.player_b, 'assistant')
                self._update_history(msg, self.player_a, 'user')

            print("MOVE_RULE Violated, skipping turn")
            return False

    def _validate_answer(self, word, player):
        # GAME RULES
        if word not in self.words_list:
            self.words_list.append(word)
            return True
        else:
            msg = f"Incorrect guess, {word} was used already, skipping turn"
            if player.name == 'Player A':
                self._update_history(msg, self.player_a, 'assistant')
                self._update_history(msg, self.player_b, 'user')
            else:
                self._update_history(msg, self.player_b, 'assistant')
                self._update_history(msg, self.player_a, 'user')

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
