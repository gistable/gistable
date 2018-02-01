import operator
import functools
import unittest
import random


class LFSR():
    def __init__(self, width, taps=None, seed=1):
        if width < 1:
            raise ValueError("Requested LFSR width < 1.")
        if taps is None:
            taps = [1]
        if max(taps) > width:
            raise ValueError("Requested LFSR tap bigger than width of LFSR.")
        if min(taps) < 1:
            raise ValueError("Requested LFSR tap less than 1.")
        if seed < 0:
            raise ValueError("Requested LFSR seed less than 0.")

        self.width = width
        self.taps = taps
        # Zero bits in seed greater than the max value of this register.
        # This assumes that silent failure is okay. Generally for my purposes it is.
        self.value = seed & (1 << width) - 1

    def tick(self):
        stream_bit = self.value & 1

        feedback_bit = 0
        for tap in self.taps:
            feedback_bit ^= (self.value >> (tap - 1)) & 1

        self.value = (self.value >> 1) | feedback_bit << (self.width - 1)

        return stream_bit


class LFSRTest(unittest.TestCase):
    INVALID_TESTCASE_WIDTHS = range(-64, 1)
    VALID_TESTCASE_WIDTHS = range(1, 64)

    def test_refuses_widths_lt_one(self):
        for width in self.INVALID_TESTCASE_WIDTHS:
            with self.subTest(width=width):
                with self.assertRaises(ValueError):
                    LFSR(width)

        for width in self.VALID_TESTCASE_WIDTHS:
            with self.subTest(width=width):
                LFSR(width)

    def test_refuses_taps_gt_width(self):
        for width in self.VALID_TESTCASE_WIDTHS:
            for tap in range(1, width + 1):
                with self.subTest(width=width, tap=tap):
                    LFSR(width, taps=[tap])

            for tap in range(width + 1, width * 2):
                with self.subTest(width=width, tap=tap):
                    with self.assertRaises(ValueError):
                        LFSR(width, taps=[tap])

    def test_refuses_taps_lt_one(self):
        for width in self.VALID_TESTCASE_WIDTHS:
            for tap in range(-64, 1):
                with self.subTest(width=width, tap=tap):
                    with self.assertRaises(ValueError):
                        LFSR(width, taps=[tap])

    def test_refuses_seed_lt_zero(self):
        for width in self.INVALID_TESTCASE_WIDTHS:
            for seed in range(-64, 0):
                with self.subTest(width=width, seed=seed):
                    with self.assertRaises(ValueError):
                        LFSR(width, seed=seed)

    def test_ticks_as_expected(self):
        l1 = LFSR(width=7, taps=[1, 7], seed=39)
        l1_exps = [1, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 0, 1, 0]
        l1_actuals = [l1.tick() for i in range(len(l1_exps))]
        with self.subTest(lfsr=1):
            self.assertEqual(l1_actuals, l1_exps)

        l2 = LFSR(width=11, taps=[1, 10], seed=365)
        l2_exps = [1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1]
        l2_actuals = [l2.tick() for i in range(len(l2_exps))]
        with self.subTest(lfsr=2):
            self.assertEqual(l2_actuals, l2_exps)

        l3 = LFSR(width=13, taps=[1, 10, 11, 13], seed=7413)
        l3_exps = [1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0]
        l3_actuals = [l3.tick() for i in range(len(l3_exps))]
        with self.subTest(lfsr=3):
            self.assertEqual(l3_actuals, l3_exps)
