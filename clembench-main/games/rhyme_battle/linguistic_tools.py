import requests
import json
import pronouncing


class RhymeValidator():
    def __init__(self, word_one, word_two) -> None:
        self.word_one = word_one.lower()
        self.word_two = word_two.lower()
        self.dm_rhyme_details = self.lookup_rhymes(word_one)
        self.final_judgement = 0

    def lookup_rhymes(self, word):
        """Makes an API call to datamuse.com

        Returns: A sorted List of JSON Objects
        """
        params = {'rel_rhy': word, 'max': 100}
        url = "https://api.datamuse.com/words"

        response = requests.get(url, params=params)
        if response.status_code == 200:
            rhymes = response.json()
            self.dm_rhyme_details = [
                {
                    "word": rhyme.get('word'),
                    "score": rhyme.get('score', 0),
                    "numSyllables": rhyme.get('numSyllables', 0)
                }
                for rhyme in rhymes
            ]

            return sorted(self.dm_rhyme_details,
                          key=lambda x: x['score'], reverse=True)
        else:
            return []

    def get_top_x_matches(self, x):
        # Look up the top x objects in the sorted JSON List
        top_x_rhymes = self.dm_rhyme_details[:x]
        return json.dumps(top_x_rhymes, indent=4)

    def validate_guess(self):
        """Check if word_two is the best match or return its rank"""
        position = 0  # Stays 0 if word not in DB
        for index, rhyme in enumerate(self.dm_rhyme_details):
            if rhyme["word"] == self.word_two:
                if index == 0:
                    # Best match
                    position = 1
                else:
                    # Returns rank in Rhymes List
                    position = index + 1
        return position

    def get_phonemes(self, word):
        phonemes = pronouncing.phones_for_word(word)
        if phonemes:
            return phonemes[0].split()
        return []

    def last_syllable_rhyme(self):
        phonemes_one = self.get_phonemes(self.word_one)
        phonemes_two = self.get_phonemes(self.word_two)

        if phonemes_one and phonemes_two:
            if phonemes_one[-1] == phonemes_two[-1]:
                return True
        return False

    def make_final_judgement(self):
        if self.validate_guess() == 1:
            self.final_judgement = 1  # Best Guess
        elif self.validate_guess() > 1:
            self.final_judgement = 2  # Second best
        else:
            # Last resort: do the last syllables of both words rhyme
            if self.last_syllable_rhyme():
                self.final_judgement = 3
        return self.final_judgement
