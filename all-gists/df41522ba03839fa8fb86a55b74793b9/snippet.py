a = open("/Users/Ron/words.txt").read().decode("utf8").split()
first_row = ["ק", "ר", "א", "ט", "ו", "ן", "ם", "פ"]
second_row = ["ש", "ד", "ג", "כ", "ע", "י", "ח", "ל", "ך", "ף"]
third_row = ["ז", "ס", "ב", "ה", "נ", "מ", "צ", "ת", "ץ"]
first_row = [x.decode("utf8") for x in first_row]
second_row = [x.decode("utf8") for x in second_row]
third_row = [x.decode("utf8") for x in third_row]

only_first = sorted([(len(x), x) for x in a if all(y in first_row for y in x)])
only_second = sorted([(len(x), x) for x in a if all(y in second_row for y in x)])
only_third = sorted([(len(x), x) for x in a if all(y in third_row for y in x)])