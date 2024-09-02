from pathlib import Path

path = Path('resources') / 'initial_prompts'

with open(path / 'initial_prompt_a.template', 'w') as file:
    file.write("Test Prompt A")

with open(path / 'initial_prompt_b.template', 'w') as file:
    file.write("Test Prompt B")

topics = ['dogs', 'cats', 'birds', 'trees']

with open(path / 'topics.txt', 'w') as file:
    for topic in topics:
        file.write(topic + '\n')
