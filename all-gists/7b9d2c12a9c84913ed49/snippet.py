import unittest
import re

class RomanToNumberConverter:
    # Validate that the input may even be processed.
    def validate(self, roman):
        if type(roman) is not str:
            raise ValueError("You must provide a string.")
        if roman == '':
            raise ValueError("An empty string was provided.")
        if len(roman) > 25:
            raise ValueError("Input string is over 25 characters.")

        roman = roman.upper()
        if not re.match('[IVXLCDM]+', roman):
            raise ValueError("Invalid roman numerals: " + roman)

    # Convert roman numerals to individual numbers to be summed up, like:
    # "DLXXXIX" -> [500, 50, 10, 10, 10, 9]
    # Subtract elements are grouped together into one number like "IX" -> 9.
    def split_roman_to_numbers(self, roman):
        numerals = {'I': 1, 'V': 5, 'X': 10, 'L': 50,
            'C': 100, 'D': 500, 'M': 1000}
        parts = []
        i = 0
        while i < len(roman):
            # Subtractions can only go back one character, be careful not to go
            # beyond the end when looking for double letter combination.
            a, b = numerals[roman[i]], 0
            if i < len(roman) - 1:
                b = numerals[roman[i + 1]]

            # A subtraction uses two characters so we should skip then next one.
            this = a
            if a < b:
                this = b - a
                i += 1

            parts.append(this)

            i += 1

        return parts

    # Roman numbers must have the hundreds, tens and ones grouped separately.
    # Make sure the numerals are in this sequence and that the total is in an
    # acceptable range.
    def validated_total(self, roman, numbers):
        if numbers != sorted(numbers, reverse=True):
            raise ValueError('Invalid roman numerals: ' + roman)

        total = sum(numbers)
        if total > 1000:
            raise ValueError("Number is larger than 1000.")

        return total

    # Convert roman numbers to a number.
    def roman_to_number(self, roman):
        self.validate(roman)
        roman = roman.upper()
        numbers = self.split_roman_to_numbers(roman)

        return self.validated_total(roman, numbers)

class TestRomanToNumber(unittest.TestCase):
    def assertError(self, msg, *args, **kwargs):
        try:
            converter = RomanToNumberConverter()
            converter.roman_to_number(*args, **kwargs)
            self.assertFail()
        except ValueError as e:
            self.assertEqual(e.message, msg)

    def test_P_is_invalid(self):
        self.assertError('Invalid roman numerals: P', 'P')

    def test_blank_string(self):
        self.assertError('An empty string was provided.', '')

    def test_invalid_type(self):
        self.assertError('You must provide a string.', 123)

    def test_string_too_long(self):
        self.assertError('Input string is over 25 characters.', 'I' * 26)

    def test_Z_is_invalid(self):
        self.assertError('Invalid roman numerals: Z', 'Z')

    def test_always_convert_to_upper_case(self):
        self.assertError('Invalid roman numerals: U', 'u')

    def assertResult(self, roman, number):
        converter = RomanToNumberConverter()
        result = converter.roman_to_number(roman)
        self.assertEquals(result, number)

    def test_I_is_1(self):
        self.assertResult('I', 1)

    def test_II_is_2(self):
        self.assertResult('II', 2)

    def test_V_is_5(self):
        self.assertResult('V', 5)

    def test_v_is_5(self):
        self.assertResult('v', 5)

    def test_VI_is_6(self):
        self.assertResult('VI', 6)

    def test_VII_is_7(self):
        self.assertResult('VII', 7)

    def test_X_is_10(self):
        self.assertResult('X', 10)

    def test_L_is_50(self):
        self.assertResult('L', 50)

    def test_C_is_100(self):
        self.assertResult('C', 100)

    def test_D_is_500(self):
        self.assertResult('D', 500)

    def test_M_is_1000(self):
        self.assertResult('M', 1000)

    def test_IV_is_4(self):
        self.assertResult('IV', 4)

    def test_IX_is_9(self):
        self.assertResult('IX', 9)

    def test_XL_is_40(self):
        self.assertResult('XL', 40)

    def test_XIX_is_19(self):
        self.assertResult('XIX', 19)

    def test_MI_is_to_large(self):
        self.assertError('Number is larger than 1000.', 'MI')

    def test_IXL_is_invalid(self):
        self.assertError('Invalid roman numerals: IXL', 'IXL')

    def test_all(self):
        ones = ('', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX')
        tens = ('', 'X', 'XX', 'XXX', 'XL', 'L', 'LX', 'LXX', 'LXXX', 'XC')
        huns = ('', 'C', 'CC', 'CCC', 'CD', 'D', 'DC', 'DCC', 'DCCC', 'CM')
        i = 0
        for h in huns:
            for t in tens:
                for o in ones:
                    if i > 0:
                        self.assertResult(h + t + o, i)
                    i += 1

# This will run the unit tests
unittest.main()
