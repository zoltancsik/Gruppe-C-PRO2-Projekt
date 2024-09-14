with open('resources/initial_prompts/level_easy/initial_prompt_a.template', 'w') as file:
    file.write(
        "Your task is to come up with a word that sounds similar to '$t_word'. "
        "Your have to reach $max_p points before the other player. "
        "Make sure your guess has the same number of syllables as '$t_word'. "
        "Your answer must follow this format: [Previous Word] -  MY GUESS: word. "
        "Your answer can not contain special characters or any other information."
        "Each round, you consider your partner's current points, "
        "Your secondary objective is to trick the other player as often as possible "
        "by using one of the following words: $wild_cards."
        "If you use a wildcard word and the other player catches you, you will be penalized."
        "Try not to use words that have been used beofe, unless you must"
)

with open('resources/initial_prompts/level_easy/initial_prompt_b.template', 'w') as file:
    file.write(
        "Your task is to come up with a word that sounds similar to what the player before you said'. "
        "Your have to reach $max_p points before the other player. "
        "Make sure your guess has the same number of syllables as '$t_word'. "
        "Your answer must follow this format: [Previous Word] -   MY GUESS: word. "
        "Your answer can not contain special characters or any other information."
        "if you think the other player is trying to trick you "
        "by using a word that is phonetically completely different than the last word, "
        "in that case you can call jinx by answering: MY GUESS: JINX."
        "Try not to use words that have been used beofe, unless you must"
)
