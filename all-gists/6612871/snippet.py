# coding=UTF-8
from __future__ import division
import nltk
from collections import Counter

# This is a simple tool for adding automatic hashtags into an article title
# Created by Shlomi Babluki
# Sep, 2013


ENGLISH_STOPWORDS = set(nltk.corpus.stopwords.words('english'))


class Hashtagify(object):

    def __init__(self, title, content):
        self.index = Counter()
        self.title = self.add_sentence_to_index(title, True)
        self.build_index(content)

    # ** Helper function for building the index
    # Stem a single token
    def stem(self, token):
        sb = nltk.stem.snowball.EnglishStemmer()
        return sb.stem(token)

    # ** Helper function for building the index
    # Split a sentence into a list of tokens
    def tokenize_sentence(self, sentence):
        tokens = nltk.word_tokenize(sentence)
        return tokens

    # ** Helper function for building the index
    # Add a single sentence into the index
    def add_sentence_to_index(self, sentence, is_title=False):
        tokens_list = []
        unstem_dic = {}
        prev_token = None

        # Split the sentence into tokens
        tokens = self.tokenize_sentence(sentence)
        for t in tokens:

            # Ignore stopwords
            if self.stem(t) in ENGLISH_STOPWORDS and not is_title:
                prev_token = None
                continue

            # Ignore words with one character (probably punctuations)
            if len(self.stem(t)) < 2:
                prev_token = None
                continue

            # *** Update the index ***

            # Unigram
            self.index[self.stem(t)] += 1

            # Bigram
            if prev_token:
                self.index["%s %s" % (prev_token, self.stem(t))] += 1
            prev_token = self.stem(t)

            tokens_list.append(self.stem(t))
            unstem_dic[self.stem(t)] = t
        return (sentence, tokens_list, unstem_dic)

    # Building the index
    def build_index(self, text):

        # Some pre-processing
        text = text.decode('utf8')
        text = text.replace(u"\u2019", "'")
        text = text.replace(u"\u2014", "-")
        text = text.replace(u"\u201c", "\"")
        text = text.replace(u"\u201d", "\"")
        text = text.replace("\n", " ")

        # Split the text into sentences
        sentences = nltk.sent_tokenize(text)

        # Add each sentence into the index
        for sentence in sentences:
            self.add_sentence_to_index(sentence.strip())

    # Special case for merging two hashtags
    # Ex. (#Social #Media) --> (#SocialMedia)
    def merge_words(self, t1, t2):
        t1 = t1.replace("#", "")
        t2 = t2.replace("#", "")
        merge = "%s %s" % (self.stem(t1), self.stem(t2))

        if self.index[merge] / self.index[self.stem(t1)] < 0.5:
            return None

        if self.index[merge] / self.index[self.stem(t2)] < 0.5:
            return None

        return "#%s%s" % (t1, t2)

    # Add hashtags to the title
    def hashtagify(self, ratio):

        # Calculate how many words to convert
        total = int(len(self.title[1]) * ratio)

        # Rank the words in the title according to the index
        ranks = []
        for t in self.title[1]:
            ranks.append((t, self.index[t]))
        sorted_ranks = sorted(
            ranks,
            key=lambda k: k[1],
            reverse=True
        )

        # Convert the most common words into hashtags
        for token in sorted_ranks[:total]:
            self.title[2][token[0]] = "#%s" % self.title[2][token[0]]

        # Rebuild the title. Merge hashtags if necessary.
        prev_tag = None
        hashtagify_title = []
        for t in self.title[1]:
            word = self.title[2][t]
            if word.startswith("#"):
                if prev_tag:
                    merged_tag = self.merge_words(prev_tag, word)
                    if merged_tag:
                        hashtagify_title.pop()
                        hashtagify_title.append(merged_tag)
                    else:
                        hashtagify_title.append(word)
                else:
                    hashtagify_title.append(word)
                prev_tag = word
            else:
                hashtagify_title.append(word)
                prev_tag = None

        return " ".join(hashtagify_title).replace(" , ", ", ").strip()


def main():

    # Demo
    # Content from: "http://techcrunch.com/2013/09/02/swayy-public-beta/"

    title = """
    Swayy Launches Into Public Beta To Curate Content For Your Social Media Audience
    """

    content = """
    While managing social media for different organizations and brands, I’ve spent hours scouring the web for relevant content to share on Twitter and Facebook. It takes a long time to find the right articles, schedule them accordingly and gauge social media reactions. Swayy, a content discovery tool, is launching its public beta to help brand managers and small businesses streamline the process down to a couple of minutes each day.

    By analyzing your posts, audience engagement and your followers’ interests, Swayy provides custom curated content that matches your brand’s image. After linking your Twitter, Facebook and LinkedIn account to the dashboard, Swayy provides a list of trending sources and topics that match your audience, so you’re tuned in to what your followers are interested in.

    But the platform’s main feature is its scrolling list of suggested content to share. Swayy crawls about 50,000 pieces of content every day from around the web, extracting key words and topics. Based on its processing engine, Swayy matches content to your trending topics and circles.

    content_dashboard

    From the social media dashboard, you can share or schedule articles on Twitter, Facebook and LinkedIn. Swayy measures the audience reactions based on retweets, responses and favorites, then adjusts its content offering accordingly. The platform also shows some basic analytics so users can track their progress over time. Co-founder Lior Degani tells me the idea is to find content to fit your audiences interests instead of your own.

    “You follow things you like to consume or things you will find interesting in the future,” he says. “We will analyze your community and provide you with the content just to feed your audience. So it will be easier to feed them, to keep your Twitter account and Facebook account and LinkedIn active with content.”

    The new public beta features some changes based on user feedback, including the ability to add your own topics and a new semantic language engine. Previously, Degani tells me, the content provided was more category-oriented, but has been altered to pick out more specific topics.

    At first glance, Swayy is a bit underwhelming, compared to similar tools such as HootSuite or Bottlenose. However, Degani tells me that Swayy is not looking to take on the social media management space, which also includes TweetDeck, Social Bro and more. Instead, Swayy is focused on becoming a content curation tool for businesses that lack a social media or branding team.

    Analytics

    The content curation market is no less crowded, with competitors such as Flipboard, Scoop.it and Pearltrees. Swayy also provides access to articles based on social media circles, but is more focused on sharing across social media outlets to gain traction with an audience. Its platform is tailored to posting content and measuring reactions.

    However, Swayy doesn’t let users browse news feeds like other social media tools, which can be a great source for content. You also can’t engage in conversations, which some brands like to do to connect with their audiences.

    Ninety-nine percent of Sway’s users have free accounts, but its premium plans range from $5/mo. to $19/mo. Swayy is in the middle of its first funding round, and has gained about 6,000 users since launching its private beta in March. Users have shared about 20,000 total articles a month using Swayy’s platform.
    """

    ht = Hashtagify(title, content)
    hashtagify_title = ht.hashtagify(0.35)
    print hashtagify_title


if __name__ == '__main__':
    main()
