from flask import Flask , render_template



app = Flask(__name__)
app.config.from_pyfile('config.py')

@app.route('/')
def entry():
    return render_template('index.html' , active='index')

# home route
@app.route("/home")
def home():
    return render_template("index.html" , active='index')


if __name__ == '__main__':
    app.run()