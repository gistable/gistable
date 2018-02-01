from flask import Flask, send_from_directory


app = Flask(__name__)


@app.route('/base/<path:filename>')
def base_static(filename):
    return send_from_directory(app.root_path + '/../static/', filename)


if __name__ == '__main__':
    app.run(debug=True)
