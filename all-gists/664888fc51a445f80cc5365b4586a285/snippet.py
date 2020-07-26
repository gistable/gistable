import bottle
import os
from bottle import default_app, route, template, request, error, response
from pbkdf2 import crypt
from beaker.middleware import SessionMiddleware
import sqlite3
import requests

# Session options
session_opts = {
    'session.type': 'memory',
    'session.cookie_expires': 400,
}

# Main route - Returns index/home template
@route('/')
def main():
    return template("/home/vcolumbia/mysite/index")

# Sign-up route - Returns signup form
@route('/signup')
def sign_up_display():
    return template("/home/vcolumbia/mysite/signup")

# Sign-up post route - Processes sign-up form via SQLite3  
@route('/signup', method="POST")
def sign_up_process():
    # Import PBKDF2 to encrypt password
    allowed_formats = [".png", ".jpg", ".jpeg"]
    email = request.forms.get("email")
    password = request.forms.get("password")
    pwhash = crypt(cpassword)
    connection = sqlite3.connect("/home/vcolumbia/mysite/ecsusers.db")
    cursor_v = connection.cursor()
    cursor_v.execute("insert into users (email, password) values (?,?)", (cemail,pwhash,))
    connection.commit()  
    avatar = request.files.data
    filename = avatar.filename
    filename_wo_ext, ext = os.path.splitext(avatar.filename)
    mapped_filename = "1" + str(ext)
    if ext not in allowed_formats:
        return "<p>Avatar must be a .png, .jpg or .jpeg only</p>"
    else:
        file_path = "/home/vcolumbia/mysite/assets/images/avatars/"
        avatar.save(file_path + mapped_filename, overwrite=True)
        return template("/home/vcolumbia/mysite/profile", filename = filename, ext = ext, filename_wo_ext = filename_wo_ext, mapped_filename = mapped_filename)

# Sign-in post route - Processes login form via SQLite3  
@route('/', method="POST")
def signin():
    # Import PBKDF2 to encrypt password
    email = request.forms.get("email")
    password = request.forms.get("password")
    connection = sqlite3.connect("/home/vcolumbia/mysite/users.db")
    c = connection.cursor()
    c.execute("SELECT * from account WHERE user_email=?", (email,))
    row = c.fetchone()
    pwhash = row[1]
    if pwhash != crypt(cepassword, pwhash):
        info = {'status': 'Invalid E-Mail or Password',
                'type': 'error'}
        return template('/home/vcolumbia/mysite/flash',info)    
    else:
        cookie = bottle.request.environ.get('beaker.session')
        cookie['logged_in'] = 1
        cookie.save()
        return bottle.redirect("/admin")

# Admin area using cookies to keep track of session
@route('/admin')
def apanel():
    cookie = bottle.request.environ.get('beaker.session')
    if 'logged_in' in cookie:
        return '''
        <p>You're logged into a session. Check your cookies!</p>
        <a href="/logout">Logout</a>

        '''
    else:
        return bottle.redirect('/')

# Logout that deletes cookie and ends session
@route('/logout')
def logout():
    cookie = bottle.request.environ.get('beaker.session')
    cookie.delete()
    return '''
    <meta http-equiv="refresh" content="2; url=/">
    <p>You are logged out. Redirecting ...</p>'''

# Show route simply returns some data from the database in a tabular format - HTML is below
@route('/show')
def show():
    return template("/home/vcolumbia/mysite/show")

# Show route simply returns some data from the database in a tabular format - HTML is below
@route('/post', method="POST")
def show_it():
    connection = sqlite3.connect("/home/vcolumbia/mysite/users.db")
    c = connection.cursor()
    c.execute("SELECT * from account")
    row = c.fetchall()
    return template("/home/vcolumbia/mysite/post", row = row)

# HTML of body for /show route 
'''
<body>
    <div class="center-div">
        <div class='blogposts'>
         % for x in row:
         <div class='post'>
             <h2>{{x[0]}}</h2>
         </div>
         % end
    </div>
</div>
</body>
'''

# Raw AJAX example - HTML is below
@route('/ajax_example')
def ajax_example():
    return template('/home/vcolumbia/mysite/ajax_example')

@route('/getinfo.json')
def ajax_example():
    text = "Greetings from the server :) without reloading it"
    return (text)

# Raw AJAX HTML page for /ajax_example above
'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width initial-scale=1.0 maximum-scale=1.0 user-scalable=yes" />
    <link rel="stylesheet" href="https://unpkg.com/purecss@1.0.0/build/pure-min.css" integrity="sha384-nn4HPE8lTHyVtfCBi5yW9d20FjT8BJwUXyWZT9InLYax14RDjBj46LmSztkmNP9w" crossorigin="anonymous">
    <title>Raw AJAX and Bottle Example</title>
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
    <link rel="icon" type="image/png" sizes="16x16" href="/static/images/col_uni.png">
    <script type="text/javascript">
    var xmlhttp;
    xmlhttp = new XMLHttpRequest();

    function GreetingText()
    {
      if (xmlhttp.readyState==4 && xmlhttp.status==200) {
        var output = xmlhttp.responseText;
        document.getElementById("info").innerHTML = output;
      }
    }

    xmlhttp.open("GET", "/getinfo.json", true);
    xmlhttp.send();
    </script>
    <style>
    body
    {
      background-color: #fcfcfc;
    }
    .center-div
    {
      text-align:center;
      position: absolute;
      margin: auto;
      top: 0;
      right: 0;
      bottom: 0;
      left: 0;
      width: 400px;
      height: 120px;
      border-radius: 3px;
    }
    button{
      margin-bottom: 8px!important;
    }
    button#red{

    }
    input{
      margin-bottom: 8px!important;
    }
    </style>
</head>

<body>
    <div class="center-div">
        <button onclick="GreetingText()" onclick="GetItems()" class="pure-button pure-button-primary">Click Me</button>
        <div id="info"></div>
    </div>
</body>
</html>
'''

# Mailgun route - change key information to your own

@route('/contact_and_resource', method='POST')
def submitr():
    subject = "Resource Submission"
    item1 =  request.forms.get('em')
    item2 =  request.forms.get('about')
    text = str(item1) + " " + str(item2)
    requests.post("https://api.mailgun.net/v3/sandboxe386fc448658564109cf88c2.mailgun.org/messages",
    auth=("api", "key-43838a85383sjd9337382e3fbd3c57d"),
    files=[("attachment", request.files.data.file)],
    data={"from": "Mailgun Sandbox <postmain@sandboxe386fc49948458js343aue94j8c2.mailgun.org>",
        "to": "Your Name <authorized_email_from__mailgun@gmail.com>",
        "subject": subject,
        "html": text})
    return '''
    <meta http-equiv="refresh" content="4; url=/">
    <p>Received - Thank you! Redirecting ...</p>
    '''

# AJAX with JQuery example - HTML below
@route('/issn')
def modulus_assignment():
    return template("/home/vcolumbia/mysite/issn")

'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width initial-scale=1.0 maximum-scale=1.0 user-scalable=yes" />
    <link rel="stylesheet" href="https://unpkg.com/purecss@1.0.0/build/pure-min.css" integrity="sha384-nn4HPE8lTHyVtfCBi5yW9d20FjT8BJwUXyWZT9InLYax14RDjBj46LmSztkmNP9w" crossorigin="anonymous">
    <title>Modulus 11 Creator</title>
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
    <link rel="icon" type="image/png" sizes="16x16" href="/static/images/col_uni.png">
    <script type="text/javascript">
        $(document).ready(function() {
            $('form').submit(function(e) {
                $.ajax({
                    type: 'POST',
                    url: '/ajax',
                    data: $(this).serialize(),
                    success: function(response) {
                        $('#ajaxP').html(response);
                    }
                });
                e.preventDefault();
            });
        });
    </script>
    <style>
    body
    {
      background-color: #fcfcfc;
    }
    .center-div
    {
      text-align:center;
      position: absolute;
      margin: auto;
      top: 0;
      right: 0;
      bottom: 0;
      left: 0;
      width: 400px;
      height: 120px;
      border-radius: 3px;
    }
    button{
      margin-bottom: 8px!important;
    }
    input{
      margin-bottom: 8px!important;
    }
    </style>
</head>
<body>
<div class="center-div">
    <form method="POST" action="/ajax">
        <input id="ajaxTextbox" name="text" type"text" /><br>
        <input id="ajaxButton" type="submit" value="Submit" class="pure-button pure-button-primary">
     <p id="ajaxP"></p>
    </form>
</div>
</body>
</html>
'''

# AJAX with JQuery route
@route('/ajax', method='POST')
def ajaxtest():
    number = request.forms.text
    if number:
        weight=10
        total = 0
        for x in number:
            value = weight * int(x)
            weight -= 1
            total =  value + total
        else:
            check = total % 11
            number = number + str(check)
            return number
    else:
        return "Nothing typed"

# Custom 404 page - Be sure to create pages for 500 and other errors
@error(404)
def error404(error):
    return "<p>404 - Page not found</p>"

#application = default_app()
application = SessionMiddleware(bottle.default_app(), session_opts)