import re
from BeautifulSoup import BeautifulSoup
import requests
url = 'http://emojicons.com/e/flipping-tables'
r = requests.get(url)
soup = BeautifulSoup(r.text)
print soup.title.string.encode('ascii', 'ignore')

print re.search( '^.*?(?=::)', soup.title.string ).group()

## gives 
## ()  :: flipping tables :: Emojicons
## (╯°□°)╯︵ ┻━┻ 
