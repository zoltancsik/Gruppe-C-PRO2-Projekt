import re
import copy
import json
from typing import List, Dict
from clemgame.clemgame import (DialogueGameMaster,
                               GameBenchmark,
                               GameScorer,
                               GameMaster)
from games.rhyme_battle.players import Guesser
from games.rhyme_battle.linguistic_tools import RhymeValidator

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
        self.rhyme_validator = None

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
        self.last_word = starting_word
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
        answer_a = self._get_answer(self.player_a)
        if not self._parse_answer(answer_a, self.player_a):
            pass
        else:
            action = {'type': 'send message', 'content': answer_a}
            self.log_event(from_='GM', to='Player 2', action=action)

        # PLAYER B
        answer_b = self._get_answer(self.player_b)
        if not self._parse_answer(answer_b, self.player_b):
            pass
        else:
            action = {'type': 'send message', 'content': answer_b}
            self.log_event(from_='GM', to='Player 1', action=action)

        self.current_turn += 1
        self.log_next_turn()
        return True

    def _get_answer(self, player):
        if player.name == self.player_a.name:
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
                'role': role,
                'content': info,
                'turn': self.current_turn,
                'points_so_far': player_obj.points
                # 'words_so_far': self.words_list
            })

        with open(f'history_{player_obj.name}.json', 'w', encoding='utf-8') as fle:
            json.dump(player_obj.history, fle, indent=4, ensure_ascii=False)

    def _parse_answer(self, answer, player):
        match = re.search(r'MY GUESS: (\w+)', answer)
        if match:
            word = match.group(1)
            if self._validate_answer(word, player):
                # Send Player's guess to player's history as assistant
                self._update_history(answer, player, 'assistant')
                # Send Player's guess to other players' history as user
                self._update_history(
                    answer,
                    self.player_b if player.name == "Player A"
                    else self.player_a, 'user')
                return True
            else:
                # GAME RULE violated
                return False
        else:
            # MOVE_RULE violated
            print("MOVE_RULE Violated")
            return False

    def _validate_answer(self, word, player):
        # GAME RULES
        if word not in self.words_list:
            if word not in WILD_CARDS and word != "CHEATER":
                self.words_list.append(word)
            elif word in WILD_CARDS and player.name == "Player A":
                if self.trick_attempt == 0:
                    self.trick_attempt = 1  # Player A tries to trick Player B
                    player.distribute_points(0.5)
                    return True
            elif word.lower() == "cheater" and player.name == "Player B":
                if self.trick_attempt == 1:
                    self.trick_attempt = 0
                    player.distribute_points(1)
                    self._update_history(f"You were caught cheating, the game goes on with {self.last_word}", self.player_a, "system")
                    self._update_history("You caught the other player cheating", player, "system")
                    return True
                else:
                    self._update_history(f"You called the other player out for cheating, but he was not. Game continues with {self.last_word}", player, "system")
                    self._update_history(f"Last turn, the other palyer falsely accused you of cheating, game continues with {self.last_word}", self.player_a, "system")
                    player.distribute_points(-0.5)
                    return False

            rhyme_validator = RhymeValidator(word, self.last_word)
            r_score = rhyme_validator.make_final_judgement()
            if r_score == 1:
                player.distribute_points(2)
                return True
            elif r_score == 2:
                player.distribute_points(1)
                return True
            elif r_score == 3:
                player.distribute_points(0.5)
                return True
            else:
                player.distribute_points(-0.5)
                self._update_history(f"My guess {word} does not rhyme with {self.last_word}", player, 'assistant')
                self._update_history(f"My guess {word} does not rhyme with {self.last_word}",
                                     self.player_b if player.name == "Player A"
                                     else self.player_a, 'user')
                return False
        else:
            player.distribute_points(-0.5)
            self._update_history(
                    f"My Guess '{word}' was invalid, word was already used | "
                    f"Guesses so far: {self.words_list}", player, "assistant")
            self._update_history(
                    f"Guess '{word}' was invalid, word was already used."
                    f"Game continues with {self.words_list[-1]} | "
                    f"Guesses so far: {self.words_list}",
                    self.player_b if player.name == "Player A"
                    else self.player_a, 'user')
            return False

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
        return ("Players must continously come up with rhyming words.")

    def create_game_master(self,
                           experiment: Dict,
                           players: List[str]
                           ) -> GameMaster:
        return RhymeBattleGameMaster(experiment, players)


class RhymeBattleGameScorer(GameScorer):
    def __init__():
        pass
