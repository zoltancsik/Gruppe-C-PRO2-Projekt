with open('resources/initial_prompts/level_easy/initial_prompt_a.template', 'w') as file:
    file.write(
        "Your task come up with a  word that likely rhymes with '$t_word', using phonetic rules. "
        "Two words rhyme if they share the same vowel in the last stressed syllable and all following sounds. "
        "Try toProvide a perfect rhyming word (exact match after the stressed vowel) or a near rhyming word (minor variations allowed)."
        "Use phonetic transcriptions similar to those in linguistic dictionaries like CMUdict."
        "Your have to reach $max_p points before the other player. "
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
        "Your task is to find a word that rhymes with the word the other player said, using phonetic rules. "
        "Two words rhyme if they share the same vowel in the last stressed syllable and all following sounds. "
        "Try toProvide a perfect rhyming word (exact match after the stressed vowel) or a near rhyming word (minor variations allowed)."
        "Use phonetic transcriptions similar to those in linguistic dictionaries like CMUdict."
        "Your have to reach $max_p points before the other player. "
        "Your answer must follow this format: [Previous Word] -   MY GUESS: word. "
        "Your answer can not contain special characters or any other information."
        "if you think the other player is trying to trick you "
        "by using a word that is phonetically completely different than the last word, "
        "in that case you can call jinx by answering: MY GUESS: JINX."
        "Try not to use words that have been used beofe, unless you must"
)
