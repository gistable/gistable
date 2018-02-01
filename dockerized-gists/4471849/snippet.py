import re
import webbrowser
import clipboard

base = 'youversion://bible?reference='
ref = clipboard.get()

book_dict = {
'Genesis': 'GEN',
'Exodus': 'EXO',
'Leviticus': 'LEV',
'Numbers': 'NUM',
'Deuteronomy': 'DEU',
'Joshua': 'JOS',
'Judges': 'JDG',
'Ruth': 'RUT',
'1 Samuel': '1SA',
'2 Samuel': '2SA',
'1 Kings': '1KI',
'2 Kings': '2KI',
'1 Chronicles': '1CH',
'2 Chronicles': '2CH',
'Ezra': 'EZR',
'Nehemiah': 'NEH',
'Esther': 'EST',
'Job': 'JOB',
'Psalms': 'PSA',
'Proverbs': 'PRO',
'Ecclesiastes': 'ECC',
'Song of Solomon': 'SNG',
'Isaiah': 'ISA',
'Jeremiah': 'JER',
'Lamentations': 'LAM',
'Ezekiel': 'EZK',
'Daniel': 'DAN',
'Hosea': 'HOS',
'Joel': 'JOL',
'Amos': 'AMO',
'Obadiah': 'OBA',
'Jonah': 'JON',
'Micah': 'MIC',
'Nahum': 'NAM',
'Habakkuk': 'HAB',
'Zephaniah': 'ZEP',
'Haggai': 'HAG',
'Zechariah': 'ZEC',
'Malachi': 'MAL',
'Matthew': 'MAT',
'Mark': 'MRK',
'Luke': 'LUK',
'John': 'JHN',
'Acts': 'ACT',
'Romans': 'ROM',
'1 Corinthians': '1CO',
'2 Corinthians': '2CO',
'Galatians': 'GAL',
'Ephesians': 'EPH',
'Philippians': 'PHP',
'Colossians': 'COL',
'1 Thessalonians': '1TH',
'2 Thessalonians': '2TH',
'1 Timothy': '1TI',
'2 Timothy': '2TI',
'Titus': 'TIT',
'Philemon': 'PHM',
'Hebrews': 'HEB',
'James': 'JAS',
'1 Peter': '1PE',
'2 Peter': '2PE',
'1 John': '1JN',
'2 John': '2JN',
'3 John': '3JN',
'Jude': 'JUD',
'Revelation': 'REV'}


p = re.compile(r'(?P<book>\w+)\s+(?P<chapter>\d+):?(?P<verse>\d+)?')
m = p.match(ref)

if m:
	youversion_ref = ''
	if m.group('book') and m.group('book') in book_dict:
		youversion_ref = book_dict[m.group('book')]
	if m.group('chapter'):
		youversion_ref += '.' + m.group('chapter')
	if m.group('verse'):
		youversion_ref += '.' + m.group('verse')

	print youversion_ref
	webbrowser.open(base + youversion_ref)
else:
	print 'No matches found.'
