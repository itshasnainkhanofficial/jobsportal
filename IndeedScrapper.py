import requests
from bs4 import BeautifulSoup
import time
import re

from Job import Job


class IndeedScrapper:
    def __init__(self, jobTitle, location):
        self.jobTitle = jobTitle
        self.location = location

    def scrape(self) -> list[Job]:
        jobs: list[Job] = []

        url = self.getUrl()

        while True:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            rawJobs = soup.find_all('div', 'jobsearch-SerpJobCard')

            for rawJob in rawJobs:
                jobs.append(self.parseRawJob(rawJob))

            #         time.sleep(4)
            # try:
            #     url = 'https://pk.indeed.com' + soup.find('a', {'aria-label': 'Next'}).get('href')
            # except AttributeError:
            break

        return jobs

    def getUrl(self):
        baseUrl = "https://pk.indeed.com/jobs?q={}&l={}"
        return baseUrl.format(self.jobTitle, self.location)

    def getDetailsUrl(self, company, location, jk):
        detailsBaseUrl = "https://pk.indeed.com/viewjob?cmp={}&t={}&jk={}"
        return detailsBaseUrl.format(company, location, jk)

    def parseRawJob(self, rawJob) -> Job:
        title = rawJob.find('h2', 'title').a.get('title')
        company = rawJob.find('span', 'company').text.strip()
        location = rawJob.find('span', 'location').text.strip()

        # this fetches value of data-jk property of the top level tag. It is used to construct a url for details of this job
        jk = rawJob.get('data-jk')
        url = self.getDetailsUrl(company, location, jk)
        textResponse = requests.get(url).text
        try:
            jobType = re.search("<p>(Job (T|t)ypes?.?(\w|\s|-|,)+)</p>", textResponse).group(1)
        except AttributeError:
            jobType = ''

        try:
            salary = rawJob.find('span', 'salaryText').text.strip()
        except AttributeError:
            salary = ''
        try:
            requirements = rawJob.find('div', 'jobCardReqItem').text.strip()
        except AttributeError:
            requirements = ''
        summary = rawJob.find('div', 'summary').text.strip()

        return Job(title=title, company=company, location=location, salary=salary, requirement=requirements,
                   summary=summary, jobType=jobType, jobLink=url, vaccancies='', lastDate='', contact='', address='')
