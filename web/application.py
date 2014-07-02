from flask import Flask
from flask import render_template
from flask import redirect

app = Flask(__name__)

GH_PAGE = "http://github.com/pczek/papr"

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/download")
def download():
    return render_template('download.html')

@app.route("/contribute")
def contribute():
    return redirect(GH_PAGE, code=302)

@app.route("/terminal")
def terminal():
    return render_template('terminal.html')

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/donate")
def donate():
    return render_template('donate.html')

if __name__ == "__main__":
    app.run(debug=True)
