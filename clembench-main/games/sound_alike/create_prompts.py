with open('resources/initial_prompts/initial_prompt_a.template', 'w') as file:
    file.write(
        "You are playing the SoundAlike Game. "
        "You must come up with phonetically similar word to $t_word. "
        "Your utterance must look like: '- $t_word is similar to (your guess)."
        "Your partner will have to answer with a new word with the same rules "
        "Consider how many syllables $t_word has, your guess must have the same amount. "
        "You are not allowed to use a word that has been used already. "
        "You will play for $nturns turns."
    )

with open('resources/initial_prompts/initial_prompt_b.template', 'w') as file:
    file.write(
        "You are playing the SoundAlike Game. "
        "Player A picked a word, you must come up with a phonetically similar word. "
        "Your utterance must look like: '- word_recieved is similar to (your guess)."
        "Your partner will have to answer with a new word with the same rules "
        "Consider how many syllables word_recieved has, your guess must have the same amount. "
        "You are not allowed to use a word that has been used already. "
        "You will play for $nturns turns."
    )
