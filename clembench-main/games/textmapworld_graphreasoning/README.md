## Text-only Map World Game - Graph Reasoning (EE-gr)

Implemented by: Yerkezhan Abdullayeva

### How to play

Instances to play are already provided in this repository. In order to run them use the following command while being in the root clembench directory:

```
python3 scripts/cli.py run -g textmapworld -m [model_to_run]
```
after running the game you can create transcripts and scores for each instance by running 
```
python3 scripts/cli.py transcribe -g textmapworld
```
and 
```
python3 scripts/cli.py score -g textmapworld
```
### Requirements

There are no other requirements than installing Networkx pyhton library


### Creating new instances

To create new instances, you need to have these files:
1. graph_generator.py: This file is only a helper function to create and store graphs.
2. instance_generator.py: This file creates instances depending on several parameters. Two files are generated:
    - Files with graphs: depending on the parameters, the name of the file is assigned and saved in the `clembech/games/textmapworld/files` directory.
    - Instance.json


Parameters applied in the instance_generator.py:
**create_new_graphs** Whether you want to create instances.json with already existing graphs or you want to create completely new graph instances, This parameter is helpful when you want to change the meta data of the instance but also want to keep the graph information as it was in the previous instances.json file. Note: If you want to create new instances but already have previous ones, you need to delete the text files with graphs from the `clembech/games/textmapworld/files` directory! Choose: True or False.
**experiments dictionary** You can control how many and what kind of experiments you want in each instance. The key is how the experiment should be called, and the value is a tuple with the size of the graph and whether there should be a cycle in the graph.
Example: "small": (4,"cycle_false").
**instance_number**: how many instances you want per experiment.
**strict** : Should the stop and move regex be strict or not. Choose: True or False.
**ambiguity** : Should the ambiguity be present in the graph. Choose: (repetition_rooms, repetition_times) or None
**game_type**: named or unnamed graph types. Choose "named_graph" or "unnamed_graph.".
**loop_reminder**: Do you want a model to be warned that it is looping in the graph? Choose: True or False.
- **max_turns_reminder** Do you want a model? Be warned that the maximum number of turns is going to be reached very soon. Choose: True or False.



### Scores

Besides the Main score that is being used for the final clemscore, other scores are also calculated.

- **Aborted** - is a binary score, indicating whether the instance was aborted at some point during the run
- **Success** - is a binary score that is 1 if all rooms have been visited and the game was not aborted
- **Lose** - is the inverse of **Success**
- **moves** - the number of moves taken by the player
- **valid_moves** - the number of valid moves taken by the player. A move is valid if there is a room in the chosen direction.
- **invalid_moves** - is difference between **moves** and **valid_moves**
- **seen** - the number of rooms seen by the player. A room has been seen if the player was in a room adjacent to it.
- **visited** - the number of rooms visited by the player
- **graph_similarity** - how similar the graph created by the player is to the actual map of that instance