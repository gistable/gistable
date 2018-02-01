import StringIO
from flask import Flask, Response


@app.route('/some_dataframe.csv')
def output_dataframe_csv():
    
    output = StringIO.StringIO()
    some_dataframe.to_csv(output)

    return Response(output.getvalue(), mimetype="text/csv")