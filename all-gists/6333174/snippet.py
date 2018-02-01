# coding=UTF-8
from __future__ import division
import nltk
import re
import requests

# Add your freebase key here
# If you don't have one, register at https://code.google.com/apis/console
FREEBASE_KEY = ""


pattern = "(?P<name>(([A-Z]+)([a-z]*)(\s)?)*)"

# I took it from
# http://stackoverflow.com/questions/4216648/facebook-pages-authoritative-list-of-categories
FACEBOOK_CATEGORIES = ["Actor/Director", "Producer", "Writer", "Musician/Band", "Author", "Editor", "Athlete", "Artist", "Public Figure", "Journalist", "News Personality", "Chef", "Lawyer", "Doctor", "Business Person", "Comedian", "Entertainer", "Teacher", "Dancer", "Politician", "Coach"]


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

    def is_person_freebase(self, possible_name):
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

    def get_facebook_result(self, possible_name):
        possible_name = possible_name.replace(" ", "")
        url = "%s/%s" % ("http://graph.facebook.com/", possible_name)
        res = requests.get(url)
        return res

    def is_person_facebook(self, name):
            res = self.get_facebook_result(name)
            data = res.json

            if data.get("first_name", ""):
                if data.get("name", "") == name:
                    return True

            if data.get("category", "") in FACEBOOK_CATEGORIES:
                if data.get("name", "") == name:
                    return True
            return False

    def is_person(self, possible_name):
        if self.is_person_freebase(possible_name):
            return True
        if self.is_person_facebook(possible_name):
            return True
        return False


# Main method, just run "python facebook_ner.py"
def main():

    # I took this article from:
    # http://thenextweb.com/apps/2013/03/21/swayy-discover-curate-content/

    text = """
        Lior Degani, the Co-Founder and head of Marketing of Swayy, pinged me last week when I was in California to tell me about his startup and give me beta access. I heard his pitch and was skeptical. I was also tired, cranky and missing my kids – so my frame of mind wasn’t the most positive.

        I went into Swayy to check it out, and when it asked for access to my Twitter and permission to tweet from my account, all I could think was, “If this thing spams my Twitter account I am going to bitch-slap him all over the Internet.” Fortunately that thought stayed in my head, and not out of my mouth.

        One week later, I’m totally addicted to Swayy and glad I said nothing about the spam (it doesn’t send out spam tweets but I liked the line too much to not use it for this article). I pinged Lior on Facebook with a request for a beta access code for TNW readers. I also asked how soon can I write about it. It’s that good. Seriously. I use every content curation service online. It really is That Good.

        What is Swayy? It’s like Percolate and LinkedIn recommended articles, mixed with trending keywords for the topics you find interesting, combined with an analytics dashboard that shows the trends of what you do and how people react to it. I like it for the simplicity and accuracy of the content curation. Everything I’m actually interested in reading is in one place – I don’t have to skip from another major tech blog over to Harvard Business Review then hop over to another major tech or business blog. It’s all in there. And it has saved me So Much Time

        Swayy Shira Abel TNW Review Articles 730x355 Swayy is a beautiful new dashboard for discovering and curating online content [Invites]

        After I decided that I trusted the service, I added my Facebook and LinkedIn accounts. The content just got That Much Better. I can share from the service itself, but I generally prefer reading the actual post first – so I end up sharing it from the main link, using Swayy more as a service for discovery.

        I’m also finding myself checking out trending keywords more often (more often than never, which is how often I do it on Twitter.com).

        Swayy Shira Abel TNW Anaytics 730x353 Swayy is a beautiful new dashboard for discovering and curating online content [Invites]

        The analytics side isn’t as interesting for me right now, but that could be due to the fact that I’ve barely been online since I came back from the US last weekend. The graphs also haven’t given me any particularly special insights as I can’t see which post got the actual feedback on the graph side (however there are numbers on the Timeline side.) This is a Beta though, and new features are being added and improved daily. I’m sure this is on the list. As they say, if you aren’t launching with something you’re embarrassed by, you’ve waited too long to launch.

        It was the suggested content that impressed me the most. The articles really are spot on – which is why I pinged Lior again to ask a few questions:

        How do you choose the articles listed on the site? Is there an algorithm involved? And is there any IP?

        Yes, we’re in the process of filing a patent for it. But basically the system works with a Natural Language Processing Engine. Actually, there are several parts for the content matching, but besides analyzing what topics the articles are talking about, we have machine learning algorithms that match you to the relevant suggested stuff. For example, if you shared an article about Zuck that got a good reaction from your followers, we might offer you another one about Kevin Systrom (just a simple example).

        Who came up with the idea for Swayy, and why? And what’s your business model?

        Our business model is a subscription model for extra social accounts (extra Facebook / Twitter, etc) and team collaboration.

        The idea was born from our day-to-day need to be active on social media, look for the best content to share with our followers, grow them, and measure what content works best.

        Who is on the team?

        Ohad Frankfurt is the CEO, Shlomi Babluki is the CTO and Oz Katz does Product and Engineering, and I [Lior Degani] do Marketing. The four of us are the founders. Oz and I were in 8200 [an elite Israeli army unit] together. Emily Engelson does Community Management and Graphic Design.

        If you use Percolate or read LinkedIn’s recommended posts I think you’ll love Swayy.

        ➤ Want to try Swayy out without having to wait? Go to this secret URL and enter the promotion code thenextweb . The first 300 people to use the code will get access.
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
