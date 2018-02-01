from gensim.models import word2vec
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

model1 = word2vec.Word2Vec.load_word2vec_format('models/glove_model.txt', binary=False)
model1.init_sims(replace=True)

from flask import Flask, jsonify, request
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/similar/<username>')
def show_user_profile(username):
    # show the user profile for that user
    n = request.args.get('topn')
    if not n:
        n = 10
    else:
        n = int(n)
        
    return jsonify(model1.most_similar([username], topn=n))

@app.route('/similarity/<word1>/<word2>')
def similarity(word1, word2):
    # show the user profile for that user
    return jsonify({"similarity": model1.similarity(word1, word2), "word1": word1, "word2": word2})

@app.route('/doesnt_match/<words>')
def doesnt_match(words):
    # show the user profile for that user
    word_list = words.split("+")
    return jsonify({"doesnt_match": model1.doesnt_match(word_list), "word_list": word_list})


if __name__ == '__main__':
    app.run()
