import os
import json
import shutil
from subprocess import call
import cld

def read_json(file_path):
    json_data = open(file_path)
    data = json.load(json_data)
    return data

def get_desc(file_path):
    data = read_json(file_path)
    description = data['extendedInfo']['description']
    return description.encode('ascii', errors='ignore') # FIXME: workaround

def get_desc_from_folder(folder_path, desc_count=1000):
    name_desc_pairs = {}
    count = desc_count
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".json"):
                if len(name_desc_pairs) < count:
                    # FIXME: unicode error \xc3\xa2\xc2\x99\xc2\xa3
                    desc = get_desc(os.path.join(root, file))
                    desc_utf8 = desc.encode('utf-8')
                    if len(desc) > 1000:
                        lang = cld.detect(desc_utf8)
                        if lang[1] == 'en' and len(lang[4]) == 1:
                            name_desc_pairs[file] = desc
    return name_desc_pairs

folder_path = "data_google_play"
if not os.path.exists(folder_path):
    call(["git", "clone", "https://github.com/sangheestyle/data_google_play.git"])

name_desc_pairs = get_desc_from_folder(folder_path)
documents = name_desc_pairs.values()

from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem.lancaster import LancasterStemmer
from nltk.cluster import KMeansClusterer, euclidean_distance
from gensim import corpora, models, utils
from numpy import array

# Step 1:
# override LdaModel for changing output format
# from [(topicid, topicvalue)] to [topicvalue] due to format of KMeansClusterer
class MyLdaModel(models.ldamodel.LdaModel):
    def __getitem__(self, bow, eps=0.01):
        is_corpus, corpus = utils.is_corpus(bow)
        if is_corpus:
            return self._apply(corpus)

        gamma, _ = self.inference([bow])
        topic_dist = gamma[0] / sum(gamma[0]) # normalize to proper distribution
        return [topicvalue for topicid, topicvalue in enumerate(topic_dist)]
                # FIXME: if topicvalue >= eps]

# Step 2: removing whitespaces, punctuations, stopwords, and stemming words
processed = []
for document in documents:
    tokenizer = RegexpTokenizer(r'\w+')
    intermediate = tokenizer.tokenize(document)
    stop = stopwords.words('english')
    intermediate = [i for i in intermediate if i not in stop]
    # FIXME: using other stemmers also to know quality of each stemmed text
    lanste = LancasterStemmer()
    intermediate = [lanste.stem(i) for i in intermediate]
    processed.append(intermediate)

# Step 3
# making dictionary and corpus
dictionary = corpora.Dictionary(processed)
#dictionary.save('/tmp/dict.dict')
corpus = [dictionary.doc2bow(description) for description in processed]
#corpora.MmCorpus.serialize('/tmp/temp.mm', corpus)

# Step 4: LDA
num_topics = 5
model_lda = MyLdaModel(corpus, id2word=dictionary, num_topics=num_topics)
doc_lda = model_lda[corpus]

'''
for doc in doc_lda:
    print doc
'''

# Step 5: k-means clustering
vectors = [array(f) for f in doc_lda]
clusterer = KMeansClusterer(num_topics, euclidean_distance, repeats=100, avoid_empty_clusters=True)
clusterer.cluster(vectors, True)

apps_per_topic = []
for x in range(num_topics):
    apps_per_topic.append([])

# classify a new vector
apk_names = name_desc_pairs.keys()
for i, doc in enumerate(doc_lda):
  topic_id = clusterer.classify(array(doc))
  apps_per_topic[topic_id].append(apk_names[i])

# Step 6: make text for each topic
text_for_topics = []
for x in range(num_topics):
    text_for_topics.append('')

apkname_stem_pairs = dict(zip(name_desc_pairs.keys(), processed))
for topic_id, names in enumerate(apps_per_topic):
    for name in names:
        # FIXME: there have two options for word cloud 1) pure descriptions 2) using stem processed
        # text_for_topics[topic_id] = text_for_topics[topic_id] + " " + name_desc_pairs[name]
        text = " ".join(apkname_stem_pairs[name])
        text_for_topics[topic_id] = text_for_topics[topic_id] + text

output_path = "out"
if os.path.exists(output_path):
    shutil.rmtree(output_path)

os.mkdir(output_path)

for topic_id, text_for_topic in enumerate(text_for_topics):
    file_name = "topic-" + str(topic_id) + ".txt"
    text_file = open(os.path.join(output_path, file_name), "w")
    text_file.write(text_for_topic)
    text_file.close()

# Step 7: word cloud - TBD
# FIXME: need to implement or just using http://www.wordle.net temporary