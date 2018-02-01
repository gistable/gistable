@app.route("/gif")
def gif():
  gif = 'R0lGODlhAQABAIAAAP///////yH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=='
  gif_str = base64.b64decode(gif)
  return send_file(io.BytesIO(gif_str), mimetype='image/gif')