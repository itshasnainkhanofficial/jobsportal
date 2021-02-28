from flask import Flask, render_template

from IndeedScrapper import IndeedScrapper
from Job import Job

app = Flask(__name__)
app.config.from_pyfile('config.py')

recentJobs: list[Job] = []
jobs: list[Job] = []


@app.route('/')
def entry():
    global recentJobs
    global jobs

    if len(recentJobs) == 0:
        indeedScrapper: IndeedScrapper = IndeedScrapper("Android Developer", '')
        recentJobs = indeedScrapper.scrape()
        print(len(recentJobs))

    return render_template('index.html', active='index', jobs=jobs, recentJobs=recentJobs)


@app.route('/about')
def about():
    return render_template('about.html', active='about')


@app.route('/contact')
def contact():
    return render_template('contact.html', active='contact')


# home route
@app.route("/home")
def home():
    return render_template("index.html", active='index')


if __name__ == '__main__':
    app.run()
