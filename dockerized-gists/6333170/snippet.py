# coding=UTF-8
from __future__ import division
import nltk
import re
import requests

# Add your freebase key here
# If you don't have one, register at https://code.google.com/apis/console
FREEBASE_KEY = ""

pattern = "(?P<name>(([A-Z]+)([a-z]*)(\s)?)*)"


class NER(object):

    def __init__(self, text, key=None):
        self.text = text
        self.sentences = self.split_text(text)
        self.results = []
        self.key = key

    def split_text(self, text):
        sentences = nltk.sent_tokenize(text)
        stripped_sentences = []
        for sentence in sentences:
            stripped_sentences.append(sentence.strip())
        return stripped_sentences

    def get_options(self):
        options = set()
        for s in self.sentences:
            f = re.finditer(pattern, s)
            for a in f:
                o = a.group("name").strip()
                parts = o.split(" ")
                if len(parts) > 1:
                    options.add(o)
                    if len(parts) > 2:
                        extra_options = nltk.ngrams(parts, 2)
                        for e in extra_options:
                            options.add(" ".join(e))

        return options

    def is_person(self, possible_name):
        # Run first with filter
        freebase_server = "https://www.googleapis.com/freebase/v1/search"
        params = {
            "query": possible_name,
            "filter": "(any type:/people/person)"
        }
        if self.key:
            params["key"] = self.key
        options = requests.get(freebase_server, params=params).json.get("result", "")
        if options:
            for option in options:
                if possible_name == option["name"]:
                    # Run without filter and validate
                    mid = option["mid"]
                    params = {"query": possible_name}
                    if self.key:
                        params["key"] = self.key
                    compare = requests.get(freebase_server, params=params).json.get("result", "")
                    for result in compare:
                        if result["mid"] == mid:
                            return True
        return False

# Main method, just run "python freebase_ner.py"
def main():

    # I took this article from:
    # http://keepingscore.blogs.time.com/2013/08/21/with-beanball-justice-baseball-makes-a-rod-sympathetic/?iid=sp-main-lead

    text = """
    If the Alex Rodriguez saga has taught sports fans anything — besides the fact that the guy has an innate ability to tune out reality and still occasionally hit a baseball very far — it’s this: when sports leagues play judge and jury, things can get mighty awkward.

    On Sunday night, Boston’s Ryan Dempster plunked Rodriguez in the ribs with a 92-m.p.h. (148 km/h) fastball, after brushing him back on one pitch, and working him inside on two others. Dempster’s intent was clear: he was drilling Rodriguez on purpose. The umps did not eject Dempster. Yankees manager Joe Girardi then went ballistic, and got tossed himself. But baseball had no choice but to discipline Dempster. On Tuesday, MLB revealed its verdict: five games and an undisclosed fine for Dempster (Girardi was also fined).

    And thus, baseball suspended one player for hitting another player that baseball has already suspended, and doesn’t want on the field.

    Baseball’s decision, on the surface, may appear noble. MLB might not like A-Rod. But a fine and suspension shows that pitchers don’t have carte blanche to peg him. Still, I don’t believe baseball went far enough. First off, beanball justice is silly and dangerous. A-Rod deserves any and all loathing. But no one deserves to be thrown out. Baseballs hurt. And beanballs are cheap shots, since batters rarely have time to dodge them. Yes, A-Rod was unharmed. But he could have gotten injured. If Dempster wanted to express his disgust at A-Rod, he could have jawed at him from the pitcher’s mound. Or picked a fight, rather than hiding behind a 92-m.p.h. dart to the ribs.

    Plus, if Dempster does not appeal, he doesn’t have to miss a start during his five-game break, since Boston has off days on Thursday and Monday. As the Providence Journal notes, if Jon Lester and Jake Peavy pitch on regular rest this weekend, Dempster can return in time for his next appearance. Plus, Dempster is still getting paid. If it weren’t for the fine — I’m guessing it won’t drain Dempster’s wallet, as he’s making $13.25 million this season — the suspension would be a vacation.

    Dempster deserves to miss a start. Would baseball have issued a tougher punishment, had A-Rod not been so contemptible? Baseball can claim equal justice for all. When baseball is in charge of both policing the game, and handing down the penalties it sees fit, fans can never know for sure.

    """

    text = text.decode("utf-8")
    ner = NER(text, FREEBASE_KEY)
    options = ner.get_options()
    people = []
    count = 0
    for option in options:
        print "%s%% Completed" % (count / len(options) * 100)
        count += 1
        if ner.is_person(option):
            people.append(option)
    print "100% Done!\n"
    print ", ".join(people)


if __name__ == '__main__':
    main()
