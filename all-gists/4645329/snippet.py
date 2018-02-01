import sleepin
import unittest

class TestSleepIn(unittest.TestCase):

  def test_valid_weekday(self):
		self.assertFalse(sleepin.sleep_in('09-02-2013'),
			"09-02-2013 is a Thursday")

	def test_valid_weekend(self):
		self.assertTrue(sleepin.sleep_in('02-02-2013'),
			"02-02-2013 is a saturday")

	def test_vacation_day(self):
		self.assertTrue(sleepin.sleep_in('02-05-2013', ['02-05-2013']),
			"02-05.2013 is a vacation day")

	def test_not_vacation_day(self):
		self.assertFalse(sleepin.sleep_in('02-05-2013', ['02-06-2013']),
			"02-05-2013 you should be at work")

if __name__ == '__main__':
	unittest.main()