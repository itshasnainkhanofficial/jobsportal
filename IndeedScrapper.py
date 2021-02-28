import asyncio

import aiohttp as aiohttp
import requests
from bs4 import BeautifulSoup, Tag
import re

from Job import Job


class IndeedScrapper:
    def __init__(self, jobTitle, location):
        self.jobTitle = jobTitle
        self.location = location

        self.currentUrl = self.getUrl()
        self.nextUrl = ''

    @staticmethod
    async def fetchJobType(job):
        async with aiohttp.ClientSession() as session:
            async with session.get(job.jobLink) as response:
                html = await response.text()
                try:
                    job.jobType = re.search("<p>(Job (T|t)ypes?.?(\w|\s|-|,)+)</p>", html).group(1)
                except AttributeError:
                    job.jobType = ''

    def scrape(self, count=None) -> list[Job]:
        jobs: list[Job] = []

        response = requests.get(self.currentUrl)
        soup = BeautifulSoup(response.text, 'html.parser')
        rawJobs = soup.find_all('div', 'jobsearch-SerpJobCard', limit=count)

        print('parsing')
        for rawJob in rawJobs:
            jobs.append(self.parseRawJob(rawJob))
        print('parsing done')

        #         time.sleep(4)
        try:
            self.nextUrl = 'https://pk.indeed.com' + soup.find('a', {'aria-label': 'Next'}).get('href')
        except AttributeError:
            self.nextUrl = ''

        print('now fetching job types')
        jobTypeTasks = []
        for job in jobs:
            jobTypeTasks.append(self.fetchJobType(job))

        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.gather(*jobTypeTasks))
        print('completed fetching job types')

        return jobs

    def getUrl(self):
        baseUrl = "https://pk.indeed.com/jobs?q={}&l={}"
        return baseUrl.format(self.jobTitle, self.location)

    @staticmethod
    def getDetailsUrl(company, location, jk):
        detailsBaseUrl = "https://pk.indeed.com/viewjob?cmp={}&t={}&jk={}"
        return detailsBaseUrl.format(company, location, jk)

    def parseRawJob(self, rawJob: Tag) -> Job:
        title = rawJob.find('h2', 'title').a.get('title')
        company = self.safeFindHtmlTag(rawJob, 'span', 'company')
        location = self.safeFindHtmlTag(rawJob, 'span', 'location')

        # this fetches value of data-jk property of the top level tag. It is used to construct a url for details of
        # this job
        jk = rawJob.get('data-jk')
        url = self.getDetailsUrl(company, location, jk)

        salary = self.safeFindHtmlTag(rawJob, 'span', 'salaryText')
        requirements = self.safeFindHtmlTag(rawJob, 'div', 'jobCardReqItem')
        summary = rawJob.find('div', 'summary').text.strip()

        return Job(title=title, company=company, location=location, salary=salary, requirement=requirements,
                   summary=summary, jobType='', jobLink=url, vaccancies='', lastDate='', contact='', address='')

    # find the text within an html tag if it exists.
    @staticmethod
    def safeFindHtmlTag(job: Tag, tagToFind, className):
        element = job.find(tagToFind, className)
        return '' if element is None else element.text.strip()

    def loadMore(self) -> list[Job]:
        self.currentUrl = self.nextUrl
        return self.scrape()
