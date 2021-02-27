from flask import Flask, render_template



app = Flask(__name__)
app.config.from_pyfile('config.py')

@app.route('/')
def entry():
    return render_template('index.html' , active='index')

@app.route('/about')
def about():
    return render_template('about.html'  , active='about')



@app.route('/contact')
def contact():
    return render_template('contact.html'  , active='contact')
# home route
@app.route("/home")
def home():
    return render_template("index.html" , active='index')


if __name__ == '__main__':
    app.run()