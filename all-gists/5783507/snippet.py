import csv

def trycast(x):
    try:
        return float(x)
    except:
        try:
            return int(x)
        except:
            return x

cols = ['beer_brewerid', 'review_time', 'review_overall', 'review_text',
        'review_aroma', 'review_appearance', 'review_profilename',
        'beer_style', 'review_palate', 'review_taste', 'beer_name',
        'beer_abv', 'beer_beerid']

f = open("beer_reviews.csv", "wb")
w = csv.writer(f)
w.writerow(cols)

doc = {}
for line in open("./beeradvocate.txt"):
    line = line.strip()
    if line=="":
        w.writerow([doc.get(col) for col in cols])
        doc = {}
    else:
        idx = line.find(":")
        key, value = tuple([line[:idx], line[idx+1:]])
        key = key.strip().replace("/", "_").lower()
        value = value.strip()
        doc[key] = trycast(value)
f.close()
 