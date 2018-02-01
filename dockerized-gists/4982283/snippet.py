from flask import Flask
app = Flask(__name__)
@app.route("/")
def hello():
    return "Hola a la Web!"
if __name__ == "__main__":
    app.run()