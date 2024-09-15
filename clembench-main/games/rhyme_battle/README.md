# Rhyme Battle
This repository contains the Rhyme Battle game, which we integrated into the ClemBench Framework as our submission for the **Programmierung II** final project. The game challenges players with phonetic wordplay in both cooperative and competitive modes.

### About the Repository
The [Workflow Documentation](https://github.com/zoltancsik/Gruppe-C-PRO2-Projekt/tree/main/workflow_documentation) folder provides an extensive insight into our work process, by including the following:
- [ClemGame UML Diagram](https://github.com/zoltancsik/Gruppe-C-PRO2-Projekt/blob/main/workflow_documentation/clem_game_uml.pdf)
- [Implementation Roadmap](https://github.com/zoltancsik/Gruppe-C-PRO2-Projekt/blob/main/workflow_documentation/implementation_roadmap.pdf)
- [Version Control Architecture](https://github.com/zoltancsik/Gruppe-C-PRO2-Projekt/blob/main/workflow_documentation/git_structure.pdf)

### Setting up the Clembench Framework
To run our game within the ClemBench framework, follow the instructions provided in [the original ClemBench repository](https://github.com/clp-research/clembench) for setting up the environment and running the framework.

### Game-Specific Setup
1. Clone the repository and navigate to the **rhyme_battle** game directory:
```bash
cd /path/to/clembench-main/games/rhyme_battle
```
2. Install the required dependencies, using:
```bash
pip install -r requirements.txt
```
3. Run the game with the following command:
```bash
python3 scripts/cli.py run -g rhyme_battle -m model_of_your_choice
```

### Game Details
You can find a more detailed description of the game in the README file located within the [game's folder](https://github.com/zoltancsik/Gruppe-C-PRO2-Projekt/tree/main/clembench-main/games/rhyme_battle).
