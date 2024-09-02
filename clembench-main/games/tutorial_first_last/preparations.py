from pathlib import Path

path = Path('resources') / 'initial_prompts'

with open(path / 'initial_prompt_a.template', 'w') as file:
    file.write(
        "Let's play a game. You must have a conversation about $topic with your partner. Your first turn must start and end with words that begin with the letter $letter. The reply of your partner must be similar, with the letter that comes after $letter in the alphabet. Then it's your turn again with the next letter, and so on. You'll do it for $nturns turns. Always start your utterance with I SAY: and then give your answer. If you break the rules, you lose."
    )

with open(path / 'initial_prompt_b.template', 'w') as file:
    file.write(
        "Let's play a game. You must have a conversation about $topic with your partner. Their first turn must start and end with words that begin with the letter $letter. Your reply must be similar, with the letter that comes after $letter in the alphabet. Then it's their turn again with the next letter, and so on. You'll do it for $nturns turns. Always start your utterance with I SAY: and then give your answer. If you break the rules, you lose."
    ) 
