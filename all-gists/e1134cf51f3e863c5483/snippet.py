@app.route('/edit/<id>' , methods=['POST', 'GET'])
def edit (id):
    #Getting user by primary key:
    post = Post.query.get(id)
    if request.method == 'POST':		
		post.title = request.form['title']
		post.text =  request.form['body']
		db.session.commit()
		return  redirect(url_for('index'))
    return render_template('edit.html', post=post)

@app.route('/delete/<id>' , methods=['POST', 'GET'])
def delete (id):
     post = Post.query.get(id)
     db.session.delete(post)
     db.session.commit()
     flash ('deleted')
	   
     return redirect(url_for('index'))