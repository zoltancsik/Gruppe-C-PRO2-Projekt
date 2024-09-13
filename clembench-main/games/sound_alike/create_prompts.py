with open('resources/initial_prompts/level_easy/initial_prompt_a.template', 'w') as file:
    file.write(
        "Your task is to come up with a word that sounds similar to '$t_word'. "
        "Your have to reach $max_p points before the other player. "
        "Make sure your guess has the same number of syllables as '$t_word'. "
        "Your answer must follow this format: [Previous Word] -  MY GUESS: word. "
        "Your answer can not contain special characters or any other information."
        "Each round, you consider your partner's current points, if you think the other player is ahead of you and you cannot win, you can use a wildcard word House. "
        "Try not to use words that have been used beofe, unless you must"
)

with open('resources/initial_prompts/level_easy/initial_prompt_b.template', 'w') as file:
    file.write(
        "Your task is to come up with a word that sounds similar to what the player before you said'. "
        "Your have to reach $max_p points before the other player. "
        "Make sure your guess has the same number of syllables as '$t_word'. "
        "Your answer must follow this format: [Previous Word] -   MY GUESS: word. "
        "Your answer can not contain special characters or any other information."
        "Each round, you consider your partner's current points, if you think the other player is ahead of you and you cannot win, you can use a wildcard word House. "
        "Try not to use words that have been used beofe, unless you must"
)
