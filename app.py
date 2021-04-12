from flask import Flask, render_template, request

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
        recentJobs = IndeedScrapper.recent()

    if len(jobs) == 0:
        IndeedScrapper.set('', 'any')
        jobs = IndeedScrapper.scrape()

    return render_template('index.html', active='index', selectedjobs=jobs, recentJobs=recentJobs)


@app.route('/about')
def about():
    return render_template('about.html', active='about')


@app.route('/contact')
def contact():
    return render_template('contact.html', active='contact')


selectedLocation = ""
indeedScrapper = ""


@app.route('/location/<loc>')
def location(loc):
    # global selectedLocation
    global recentJobs
    global jobs

    # selectedLocation = loc
    IndeedScrapper.set(IndeedScrapper.jobTitle, loc)
    jobs = IndeedScrapper.scrape()

    return render_template('index.html', active='index', selectedjobs=jobs, recentJobs=recentJobs)


@app.route('/title', methods=['POST'])
def title():
    searchTitle = request.form['search-product']
    IndeedScrapper.set(searchTitle, IndeedScrapper.location)
    global jobs
    jobs = IndeedScrapper.scrape()

    return render_template('index.html', active='index', selectedjobs=jobs, recentJobs=recentJobs)


@app.route("/loadmore")
def loadmore():
    global jobs
    jobs = IndeedScrapper.loadMore()
    return render_template('index.html', active='index', selectedjobs=jobs, recentJobs=recentJobs)


# home route
@app.route("/home")
def home():
    return render_template("index.html", active='index')



if __name__ == '__main__':
    app.run()
