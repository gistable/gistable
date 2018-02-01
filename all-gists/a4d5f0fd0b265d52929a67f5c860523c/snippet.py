import unittest

def find_anagrams(list_of_strings, word):
    # your implementation here
    anagrams = []
    for i in list_of_strings:
        if ' '.join(sorted(word)) == ' '.join(sorted(i)):
            anagrams.append(i)
    return anagrams
    
class AnagramsTestCase(unittest.TestCase):
    # implement at least 3 test cases
    def test_one(self):
        self.assertEqual(find_anagrams(["east", "seat", "teas", "bears", "eat"], "eats")

    def test_two(self):
        self.assertEqual(find_anagrams(["cheaters", "seat", "teachers", "teach", "lol"], "eats")

    def test_three(self):
        self.assertEqual(find_anagrams(["lead", "deal", "hand", "led", "leader"], "lead")