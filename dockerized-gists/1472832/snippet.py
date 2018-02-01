from flask import Flask
from flask import request
app = Flask(__name__)

#Normally this would be an external file like object, but here
#it's inlined
FORM_PAGE = """
    <html>
        <head>
            <title>Flask Form</title>
        </head>
        <body>
            <form action="/process" method="POST">
                <label>Name</label>
                <input name="user_name" />
                <br/>
                
                <label>Age</label>
                <input type="range" name="user_age" />
                <br/>
                
                <fieldset>
                    <legend>Drink preferences</legend>
                
                    <label>Coffee, Tea, water?</label><br/>
                    <input type="checkbox" name="drink_type[]" value="coffee" /> Coffee  <br/>
                    <input type="checkbox" name="drink_type[]" value="tea" /> Tea  <br/>
                    <input type="checkbox" name="drink_type[]" value="water" /> Water  <br/>
                    
                    <label>Temperature</label><br />
                    <input type="radio" name="drink_temp" value="hot" /> Hot <br/>
                    <input type="radio" name="drink_temp" value="warm" /> Warm <br/>
                    <input type="radio" name="drink_temp" value="Cold" /> Cold <br/>
                    <input type="radio" name="drink_temp" value="Iced" /> Iced <br/>
                </fieldset>
                    
                
                <input type="submit" />                
            </form>
    </html>
"""


@app.route('/')
def home_form():
    return FORM_PAGE

@app.route("/process", methods = ["GET", "POST"] )
def process_form():
    formData = request.values if request.method == "GET" else request.values
    response = "Form Contents <pre>%s</pre>" % "<br/>\n".join(["%s:%s" % item for item in formData.items()] )
    return response

if __name__ == '__main__':
    app.run()