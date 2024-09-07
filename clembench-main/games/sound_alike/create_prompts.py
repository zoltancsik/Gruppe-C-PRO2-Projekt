from pathlib import Path

path = Path('resources') / 'initial_prompts'

with open(path / 'initial_prompt_a.template', 'w') as file:
    file.write(
        "You are playing the SoundAlike Game."
        "You must come up with a word that is phonetically similar to $word"
        "Your utterance must look like: your_word is similar to $word"
        "give your answer. If you break the rules, you lose."
    )

with open(path / 'initial_prompt_b.template', 'w') as file:
    file.write(
        "You are playing the SoundAlike Game."
        "You must come up with a word that is phonetically similar to $word"
        "Your utterance must look like: your_word is similar to $word"
        "give your answer. If you break the rules, you lose."
    )
