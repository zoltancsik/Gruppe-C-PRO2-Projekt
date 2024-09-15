# Rhyme Battle - README

## Overview

This folder contains the game **Rhyme Battle**, designed to work within the ClemBench Framework. The game is a rhyming challenge where two players, Player A and Player B, take turns coming up with rhyming words based on the game's difficulty. Players win by accumulating enough points or lose if they exceed the number of allowed turns. The game can be played in different difficulty levels: **EASY**, **HARD**, and **CO-OP**.

## Game Structure

### Classes

- **RhymeBattleGameMaster**: The main class responsible for setting up and managing the game logic, including player turns, point distribution, and handling of game events.
- **RhymeBattleScorer**: This class handles the scoring of the game, calculating the request counts, validated guesses, and success ratios for each game instance.
- **RhymeBattleGameBenchmark**: Defines the game’s properties and integrates it with the ClemBench Framework.
- **RhymeBattleInstanceGenerator**: Creates the instances that serve as a base for each game 
- **PromptGenerator**: Writes prompts into resources/initial_prompts/lvl/prompt_player.template

### Key Features

- **Guesser Class**: Player models, `Player A` and `Player B`, make guesses for rhyming words. Each player's performance is evaluated based on the validity and rhyme quality of their responses.
- **API-Based Rhyme Validation**: Utilizes the `RhymeValidator` class to check if the guessed word rhymes with the last word in the turn.
- **Logging and History**: The game logs every event, including player actions, game state, and evaluations. Histories of each player can be stored in JSON format for further inspection.
- **Points and Game Metrics**: Players earn points based on the difficulty of the game and the accuracy of their rhymes.

## Game Difficulties

1. **EASY**: Players are required to guess simple rhyming words, first one to reach points_needed wins.
2. **HARD**: Players must guess rhymes at the end of sentences, with stricter validation rules.
3. **CO-OP**: Players work together to reach a common goal, sharing points but following similar rules to the HARD mode.

## Dependencies

- Python 3.x
- `clemgame` module for game integration
- JSON for saving and reading player histories
- Regular expressions (`re`) for parsing player input
- `requests` and `pronouncing` Libraries
