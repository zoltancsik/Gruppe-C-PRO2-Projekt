import re
import copy
import json
from typing import List, Dict
from clemgame import metrics as ms
from clemgame.clemgame import (DialogueGameMaster,
                               GameBenchmark,
                               GameScorer,
                               GameMaster)
from games.rhyme_battle.players import Guesser
from games.rhyme_battle.linguistic_tools import RhymeValidator

GAME_NAME = "rhyme_battle"
WILD_CARDS = ["Appreciation", "Inauguration", "Consideration"]
LET_INSPECT = True  # Write players' histories to resources/histories


class RhymeBattleGameMaster(DialogueGameMaster):
    def __init__(self, experiment: Dict, players: List[str]):
        super().__init__(GAME_NAME, experiment, players)

        # PLAYER + INSTANCE INFOS
        self.model_a = players[0]
        self.model_b = players[1]
        self.complete_turns: int = 0
        self.words_list = []

        # ATTRIBUTES FOR METRICS
        self.aborted: bool = False
        self.lose: bool = False
        self.win: bool = False

        # DEPENDENT CLASSES
        self.rhyme_validator = None
        self.scorer = None

    def setup(self, init_prompt_a, init_prompt_b,
              n_turns, difficulty,
              game_id, starting_word,
              points_needed):

        # SETUP PLAYERS + PROMPTS
        self.player_a = Guesser(self.model_a, 'Player A', 0)
        self.player_b = Guesser(self.model_b, 'Player B', 0)
        self.difficulty = difficulty
        self.words_list.append(starting_word)
        self.points_needed = points_needed
        self.points = 0
        self.trick_attempt = 0

        # INGAME METRICS
        self.n_turns = n_turns
        self.starting_word = starting_word
        self.last_word = starting_word
        self.game_id = game_id
        self.current_turn = 0

        # API CALL METRICS
        self.request_counts = [0] * (n_turns + 1)
        self.parsed_request_counts = [0] * (n_turns + 1)
        self.violated_request_counts = [0] * (n_turns + 1)

        # PREP SCORING
        self.scorer = RhymeBattleScorer(self.experiment, self.__dict__)

        # LOG GAME DATA
        self.log_next_turn()
        self.log_event(from_='GM',
                       to='GM',
                       action={
                        'type': 'system',
                        'content':
                          f"Game setup: difficulty={self.difficulty}, "
                          f"Points needed={self.points_needed}, "
                          f"Turns={self.n_turns}"})
        self.log_players({'GM': 'RhymeBattle GameMaster',
                          'Player A': f'{self.model_a}',
                          'Player B': f'{self.model_b}'})
        action = {'type': 'send message', 'content': init_prompt_a}
        self.log_event(from_='GM', to='Player 1', action=action)
        action = {'type': 'send message', 'content': init_prompt_b}
        self.log_event(from_='GM', to='Player 2', action=action)
        self.log_key('starting_word', self.starting_word)

        # UPDATE HISTORIES
        self._update_history(init_prompt_a, self.player_a, 'system')
        self._update_history(init_prompt_b, self.player_b, 'system')

    def play(self) -> None:
        # MAIN GAME LOOP
        while self.turn():
            if self.difficulty == "CO-OP":
                # PLAYERS REACH POINTS_NEEDED TOGETHER
                if self.player_a.get_points() + \
                   self.player_b.get_points() >= self.points_needed:
                    self.win = True
                    # LOG WIN
                    self.log_event(from_='GM',
                                   to='GM',
                                   action={
                                        'type': 'system',
                                        'content': 'Max Points Reached.'
                                                   'The game is over'})
                    break
            else:
                # PLAYER A OR B REACHES POINTS_NEEDED
                if self.player_a.points >= self.points_needed or \
                   self.player_b.points >= self.points_needed:
                    self.win = True
                    # LOG WIN
                    winner = 'Player A' if self.player_a.get_points() > \
                        self.player_b.get_points() else 'Player B'
                    self.log_event(from_='GM',
                                   to='GM',
                                   action={
                                    'type': 'system',
                                    'content': f"Max points achieved by "
                                               f"{winner}. Game Over"})
                    break
                # MAX_TURNS REACHED
                elif self.current_turn >= self.n_turns:
                    self.lose = True
                    # LOG LOSS
                    self.log_event(from_='GM',
                                   to='GM',
                                   action={
                                    'type': 'system',
                                    'content': 'Max Turns reached. Game Over'})
                    break

        # LOG API DETAILS
        self.log_key("request_counts", self.request_counts)
        self.log_key("parsed_request_counts", self.parsed_request_counts)
        self.log_key("violated_request_counts", self.violated_request_counts)
        # LOG GAME ENDING
        self.log_event(from_='GM',
                       to='GM',
                       action={
                           'type': 'system',
                           'content':
                               f"Game Ending: {'Win' if self.win else 'Loss'} "
                               f"Total Turns: {self.current_turn}, "
                               "Final Points: "
                               f"A:{self.player_a.points}, "
                               f"B:{self.player_b.points}"})

        # CREATE DICT FOR - AND CALL COMPUTE_SCORES
        episode_interactions = {
            "turns": self.current_turn,
            "request_counts": self.request_counts,
            "parsed_request_counts": self.parsed_request_counts,
            "violated_request_counts": self.violated_request_counts
        }
        if self.scorer:
            self.scorer.compute_scores(episode_interactions)

        print("====================[GAME OVER]====================") # FIXME: REMOVE
        print(f"POINTS: A:{self.player_a.points} B: "
              f"{self.player_b.points}/{self.points_needed} "
              f"ROUNDS: {self.current_turn}/{self.n_turns}")
        action = {'type': 'info', 'content': 'end game'}
        self.log_event(from_='GM', to='GM', action=action)
        self.log_eval_assets()

    def turn(self):
        # PLAYER A
        answer_a = self._get_answer(self.player_a)
        self.request_counts[self.current_turn] += 1
        if not self._parse_answer(answer_a, self.player_a):
            # MOVE_RULE OR GAME_RULE VIOLATED
            self.violated_request_counts[self.current_turn] += 1
            pass
        else:
            # VALID MOVE
            self.parsed_request_counts[self.current_turn] += 1
            self.log_event(from_='GM',
                           to='Player B',
                           action={
                               'type': 'send message',
                               'content': answer_a})
        # PLAYER B
        self.request_counts[self.current_turn] += 1
        answer_b = self._get_answer(self.player_b)

        if not self._parse_answer(answer_b, self.player_b):
            # MOVE_RULE OR GAME_RULE VIOLATED
            self.violated_request_counts[self.current_turn] += 1
            pass
        else:
            # VALID MOVE
            self.parsed_request_counts[self.current_turn] += 1
            self.log_event(from_='GM',
                           to='Player A',
                           action={
                               'type': 'send message',
                               'content': answer_b})
        self.current_turn += 1
        self.log_next_turn()
        return True

    def _get_answer(self, player):
        if player.name == self.player_a.name:
            # APPEND HISTORY TO PROMPT THROUGH __call__ METHOD
            prompt, raw_answer, answer = self.player_a(
                self.player_a.history,
                self.n_turns
            )
            self.log_event(from_='Player A',
                           to='GM',
                           action={'type': 'get message', 'content': answer},
                           call=(copy.deepcopy(prompt), raw_answer))
            # FIXME: REMOVE
            print("\n")
            print(f"===[ TURN: {self.current_turn}/{self.n_turns} |"
                  f" LVL: {self.difficulty} | "
                  f"POINTS: A:{self.player_a.points}|B:{self.player_b.points}"
                  f"/{self.points_needed}]===")
            print(f"A - {self.player_a.model}: {answer}")
        else:
            # APPEND HISTORY TO PROMPT THROUGH __call__ METHOD
            prompt, raw_answer, answer = self.player_b(
                self.player_b.history,
                self.n_turns
            )
            self.log_event(from_='Player B',
                           to='GM',
                           action={'type': 'get message', 'content': answer},
                           call=(copy.deepcopy(prompt), raw_answer))
            print(f"B - {self.player_b.model}: {answer}")  # FIXME: REMOVE

        if not answer:
            # REQUEST FAIL
            self.log_event(from_='GM',
                           to=player.name,
                           action={
                            'type': 'system',
                            'content': 'No valid answer received.'})
        return answer

    def _update_history(self, info, player, role, export_json=LET_INSPECT):
        # APPEND STATS TO PLAYER HISTORY + OPTIONALLY WRITE TO JSON
        player.history.append(
            {
                'role': role,
                'content': info,
                'turn': self.current_turn,
                'points_so_far': player.points
            })
        # OPTIONAL - TO INSPECT HISTORIES
        if export_json:
            h_path = (
                'games/rhyme_battle/resources'
                f'/player_histories/{player.name}.json')
            self.store_file(player.history, h_path)

    def store_file(self, data, path):
        # OVERWRITING SUPER METHOD FOR PRETTY PRINT
        with open(path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, indent=4, ensure_ascii=False)
        self.logger.info("Game file stored to %s", path)

    def _parse_answer(self, answer, player):
        if self.difficulty == "EASY":
            # ENFORCE MOVE RULE
            match = re.search(r'MY GUESS: (\w+)', answer)
            if match:
                word = match.group(1)
                # ENFORCE GAME_RULE
                if self._validate_answer(word, player):
                    # LOG ANSWER TO BOTH PLAYERS
                    self._update_history(answer, player, 'assistant')
                    self._update_history(answer,
                                         self.player_b if
                                         player.name == "Player A" else
                                         self.player_a, 'user')
                    return True
                else:
                    # GAME_RULE VIOLATED
                    self.log_event(from_='GM',
                                   to=player.name,
                                   action={
                                    'type': 'system',
                                    'content': 'Answer is incorrect.'})
                    return False
            else:
                # MOVE_RULE VIOLATED
                self.log_event(from_='GM',
                               to=player.name,
                               action={
                                'type': 'system',
                                'content': 'Answer is incorrect format.'})
                return False

        elif self.difficulty == "HARD":
            pattern = r'\b\w+\b(?=[^\w]*$)'
            word = re.search(pattern, answer)
            # ENFORCE MOVE_RULE
            if word:
                # ENFORCE GAME_RULE
                if self._validate_hard_answer(answer, word.group(), player):
                    return True
                else:
                    # GAME_RULE VIOLATED
                    self.log_event(from_='GM',
                                   to=player.name,
                                   action={
                                        'type': 'system',
                                        'content': 'Answer is incorrect:'
                                                   'Last word does not rhyme'})
                    return False
            else:
                # MOVE_RULE VIOLATED
                self.log_event(from_='GM',
                               to=player.name,
                               action={
                                'type': 'system',
                                'content': 'Answer is incorrect format:'
                                           'Not string'})
                return False

        elif self.difficulty == "CO-OP":
            # ENFORCE MOVE_RULE
            if isinstance(answer, str):
                # ENFORCE GAME_RULE
                if self._validate_coop_answer(answer, player):
                    return True
                else:
                    self.log_event(from_='GM',
                                   to=player.name,
                                   action={
                                     'type': 'system',
                                     'content': 'Answer is incorrect.'})
                    return False
            else:
                # MOVE_RULE VIOLATED
                self.log_event(from_='GM',
                               to=player.name,
                               action={
                                'type': 'system',
                                'content': 'Answer is invalid format.'
                                      }
                               )
                return False

    def _validate_coop_answer(self, answer, player):
        rhyme_validator = RhymeValidator(answer, self.starting_word)
        r_score = rhyme_validator.make_final_judgement()
        # WORDS DO NOT RHYME
        if r_score == 0:
            reason = f"{answer} does not rhyme with {self.starting_word}"
            return False
        # WORD ALREADY USED
        elif answer in self.words_list:
            reason = f"{answer} was already used once"
            return False
        # CORRECT GUESS
        else:
            reason = answer
            final_points = 2 if r_score == 1 else 1 if r_score == 2 else 0.5
            player.distribute_points(final_points)
            self.words_list.append(answer)
        self._update_history(reason, player, 'assistant')
        self._update_history(reason,
                             self.player_b if player.name == "Player A"
                             else self.player_a, 'user')
        return True

    def _validate_hard_answer(self, answer, word, player):
        rhyme_validator = RhymeValidator(word, self.last_word)
        r_score = rhyme_validator.make_final_judgement()
        # END OF SENTENCE WORDS DON'T RHYME
        if r_score == 0:
            self.log_event(from_='GM',
                           to=player.name,
                           action={'type': 'system',
                                   'content': f"Invalid: {word} does not"
                                              f" rhyme with {self.last_word}"})
            self._update_history(f"Invalid, continue with {self.last_word}",
                                 player,
                                 'assistant')
            self._update_history(f"Invalid, continue with {self.last_word}",
                                 self.player_b if player.name == "Player A"
                                 else self.player_a,
                                 'user')
            player.distribute_points(-0.5)
            return False
        # CORRECT GUESS
        else:
            final_points = 2 if r_score == 1 else 1 if r_score == 2 else 0.5
            player.distribute_points(final_points)

        self.last_word = word
        self._update_history(answer, player, 'assistant')
        self._update_history(answer, self.player_b if player.name == "Player A"
                             else self.player_a, 'user')
        return True

    def _validate_answer(self, word, player):
        if word not in self.words_list:
            # RESTRICT APPEND TO NON WILDCARD WORDS
            if word not in WILD_CARDS and word != "CHEATER":
                self.words_list.append(word)

            # PLAYER A TRIES TO TRICK PLAYER B
            elif word in WILD_CARDS and player.name == "Player A":
                if self.trick_attempt == 0:
                    self.trick_attempt = 1
                    player.distribute_points(0.5)
                    return True

            # PLAYER B ACCUSES PLAYER A OF CHEATING
            elif word.lower() == "cheater" and player.name == "Player B":
                if self.trick_attempt == 1:
                    self.trick_attempt = 0
                    player.distribute_points(1)
                    self._update_history("You were caught cheating, "
                                         "the game goes on "
                                         f"with {self.last_word}",
                                         self.player_a, "system")
                    self._update_history("Caught the other player cheating",
                                         player, "system")
                    return True
                else:
                    # PLAYER B FALSELY CALLS PLAYER A OUT
                    self._update_history("Called other player out for cheating"
                                         " , but they were not. Game continues"
                                         f" with {self.last_word}",
                                         player, "system")
                    self._update_history("Falsely accused of cheating, game"
                                         f" continues with {self.last_word}",
                                         self.player_a, "system")
                    player.distribute_points(-0.5)
                    return False

            rhyme_validator = RhymeValidator(word, self.last_word)
            r_score = rhyme_validator.make_final_judgement()

            # RHYMES, IF r_score >= 1, DIRECT MATCH IN DATABASE - BEST GUESS
            # IF r_score == 0.5 ONLY LAST SYLLABLES RHYME
            if r_score >= 1:
                f_points = 2 if r_score == 1 \
                      else 1 if r_score == 2 \
                      else 0.5
                player.distribute_points(f_points)
            # WORDS DON'T RHYME
            else:
                self.log_event(from_='GM',
                               to=player.name,
                               action={'type': 'system',
                                       'content': f"'{word}' is not a rhyme."})
                self._update_history(f"Invalid: {word} does not rhyme with"
                                     f"{self.last_word}",
                                     player, 'assistant')
                self._update_history(f"Invalid: {word} does not rhyme with"
                                     f"{self.last_word}",
                                     self.player_b if player.name == "Player A"
                                     else self.player_a, 'user')
                player.distribute_points(-0.5)
                return False
        else:
            # WORD ALREADY USED
            player.distribute_points(-0.5)
            self.log_event(from_='GM',
                           to=player.name,
                           action={
                            'type': 'system',
                            'content': f"'{word}' Already Guessed."})
            self._update_history(f"Invalid: {word}' was already used | "
                                 f"Guesses so far: {self.words_list}",
                                 player, "assistant")
            self._update_history(f"Invalid: {word}' was already used."
                                 f"Game continues with {self.words_list[-1]} |"
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
        return (
            "Players must continously come up with rhyming words "
            "or sentences or word chains, based on game difficulty"
            )

    def create_game_master(self,
                           experiment: Dict,
                           players: List[str]
                           ) -> GameMaster:
        return RhymeBattleGameMaster(experiment, players)

    def create_game_scorer(self,
                           experiment: Dict,
                           game_instance: Dict) -> GameScorer:
        return RhymeBattleScorer(experiment, game_instance)


class RhymeBattleScorer(GameScorer):
    def __init__(self, experiment: Dict, game_instance: Dict):
        super().__init__(GAME_NAME, experiment, game_instance)

    def compute_scores(self, episode_interactions: Dict) -> None:
        all_turn_scores = []
        request_counts = episode_interactions["request_counts"]
        parsed_request_counts = episode_interactions["parsed_request_counts"]
        violated_request_counts = episode_interactions["violated_request_counts"]

        for turn_idx in range(len(request_counts)):
            turn_score_dict = {
                "request_counts": request_counts[turn_idx],
                "parsed_request_counts": parsed_request_counts[turn_idx],
                "violated_request_counts": violated_request_counts[turn_idx]
            }

            self.log_turn_score(turn_idx, ms.METRIC_REQUEST_COUNT, turn_score_dict["request_counts"])
            self.log_turn_score(turn_idx, ms.METRIC_REQUEST_COUNT_PARSED, turn_score_dict["parsed_request_counts"])
            self.log_turn_score(turn_idx, ms.METRIC_REQUEST_COUNT_VIOLATED, turn_score_dict["violated_request_counts"])
            all_turn_scores.append(turn_score_dict)

        total_request_count = sum(
            [turn["request_counts"] for turn in all_turn_scores])
        total_parsed_request_count = sum(
            [turn["parsed_request_counts"] for turn in all_turn_scores])
        total_violated_request_count = sum([turn["violated_request_counts"] for turn in all_turn_scores])

        self.log_episode_score(ms.METRIC_REQUEST_COUNT, total_request_count)
        self.log_episode_score(ms.METRIC_REQUEST_COUNT_PARSED, total_parsed_request_count)
        self.log_episode_score(ms.METRIC_REQUEST_COUNT_VIOLATED, total_violated_request_count)

        request_success_ratio = round(total_parsed_request_count / float(total_request_count), 4)
        self.log_episode_score(ms.METRIC_REQUEST_SUCCESS, request_success_ratio)

        if episode_interactions.get('aborted', False):
            self.log_episode_score(ms.METRIC_ABORTED, 1)
            self.log_episode_score(ms.METRIC_LOSE, 0)
            self.log_episode_score(ms.METRIC_SUCCESS, 0)
            self.log_episode_score(ms.BENCH_SCORE, 0)
        elif episode_interactions.get('win', True):
            self.log_episode_score(ms.METRIC_SUCCESS, 1)
            self.log_episode_score(ms.METRIC_ABORTED, 0)
            self.log_episode_score(ms.METRIC_LOSE, 0)
            self.log_episode_score(ms.BENCH_SCORE, 100)
        elif episode_interactions.get('lose', True):
            self.log_episode_score(ms.METRIC_SUCCESS, 0)
            self.log_episode_score(ms.METRIC_ABORTED, 0)
            self.log_episode_score(ms.METRIC_LOSE, 1)
            self.log_episode_score(ms.BENCH_SCORE, 0)
