from flask import Flask
app = Flask(__name__)


@app.route("/")
def hello():
    return ("Failed Dependency", 424, {})


if __name__ == "__main__":
    app.run(debug=True)
