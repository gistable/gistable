import re

class PasswordValidator:

    LOWER_LETTERS = '[a-z]'
    UPPER_LETTERS = '[A-Z]'
    NUMBERS = '[0-9]'
    SPECIAL_CHARACTERS = '[%#]'

    def __init__(self, minimumLength):
        self.minimumLength = minimumLength

    def isStrongPassword(self, password):
        hasMinimumLength = len(password) >= self.minimumLength
        hasLowerLetters = self.hasAny(self.LOWER_LETTERS, password)
        hasUpperLetters = self.hasAny(self.UPPER_LETTERS, password)
        hasNumbers = self.hasAny(self.NUMBERS, password)
        hasSpecialChars = self.hasAny(self.SPECIAL_CHARACTERS, password)
        return hasMinimumLength and hasLowerLetters and hasUpperLetters and hasNumbers and hasSpecialChars

    @staticmethod
    def hasAny(pattern, password):
        return re.search(pattern, password) is not None
