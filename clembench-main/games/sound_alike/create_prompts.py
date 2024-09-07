with open('resources/initial_prompts/initial_prompt_a.template', 'w') as file:
    file.write(
        "You are playing the SoundAlike Game. "
        "You must come up with phonetically similar word to $t_word. "
        "Your utterance must look like: 'your guess is similar to $t_word. "
        "Your partner will have to answer with a new word with the same rules "
        "Give your answer. If you break the rules, you lose. "
        "You will play for $nturns turns."
    )

with open('resources/initial_prompts/initial_prompt_b.template', 'w') as file:
    file.write(
        "You are playing the SoundAlike Game. "
        "You must come up with phonetically similar word to $t_word. "
        "Your utterance must look like: 'your guess is similar to $t_word. "
        "Your partner will have to answer with a new word with the same rules "
        "Give your answer. If you break the rules, you lose. "
        "You will play for $nturns turns."
    )
