import asyncio

import aiohttp as aiohttp
import requests
from bs4 import BeautifulSoup, Tag
import re

from Job import Job


class IndeedScrapper:
    currentUrl = ''
    nextUrl = ''
    jobTitle = ''
    location = ''

    @staticmethod
    def set(title, location):
        IndeedScrapper.jobTitle = title
        IndeedScrapper.location = location

        IndeedScrapper.currentUrl = IndeedScrapper.getUrl(title, location)

    @staticmethod
    async def fetchJobType(job):
        async with aiohttp.ClientSession() as session:
            async with session.get(job.jobLink) as response:
                html = await response.text()
                try:
                    job.jobType = re.search("<p>(Job (T|t)ypes?.?(\w|\s|-|,)+)</p>", html).group(1)
                except AttributeError:
                    job.jobType = ''

    @staticmethod
    def recent(count=3):
        url = IndeedScrapper.getUrl('', 'any')
        return IndeedScrapper._scrape(count, url)

    @staticmethod
    def scrape() -> list[Job]:
        return IndeedScrapper._scrape(None, IndeedScrapper.currentUrl, True)

    @staticmethod
    def _scrape(count, url, storeNextUrl=False) -> list[Job]:
        print("scraping from: ", url)
        jobs: list[Job] = []

        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        rawJobs = soup.find_all('div', 'jobsearch-SerpJobCard', limit=count)

        print('parsing')
        for rawJob in rawJobs:
            jobs.append(IndeedScrapper.parseRawJob(rawJob))
        print('parsing done')

        if storeNextUrl:
            try:
                IndeedScrapper.nextUrl = 'https://pk.indeed.com' + soup.find('a', {'aria-label': 'Next'}).get('href')
            except AttributeError:
                IndeedScrapper.nextUrl = ''

        return jobs

    @staticmethod
    def getUrl(title, location):
        baseUrl = "https://pk.indeed.com/jobs?q={}&l={}"
        return baseUrl.format(title, location)

    @staticmethod
    def getDetailsUrl(company, location, jk):
        detailsBaseUrl = "https://pk.indeed.com/viewjob?cmp={}&t={}&jk={}"
        return detailsBaseUrl.format(company, location, jk)

    @staticmethod
    def parseRawJob(rawJob: Tag) -> Job:
        title = rawJob.find('h2', 'title').a.get('title')
        company = IndeedScrapper.safeFindHtmlTag(rawJob, 'span', 'company')
        location = IndeedScrapper.safeFindHtmlTag(rawJob, 'span', 'location')

        # this fetches value of data-jk property of the top level tag. It is used to construct a url for details of
        # this job
        jk = rawJob.get('data-jk')
        jobLink = IndeedScrapper.getDetailsUrl(company, location, jk)

        salary = IndeedScrapper.safeFindHtmlTag(rawJob, 'span', 'salaryText')
        requirements = IndeedScrapper.safeFindHtmlTag(rawJob, 'div', 'jobCardReqItem')
        summary = rawJob.find('div', 'summary').text.strip()

        return Job(title=title, company=company, location=location, salary=salary, requirement=requirements,
                   summary=summary, jobType='', jobLink=jobLink, vaccancies='', lastDate='', contact='', address='',
                   dataJk=jk)

    # find the text within an html tag if it exists.
    @staticmethod
    def safeFindHtmlTag(job: Tag, tagToFind, className):
        element = job.find(tagToFind, className)
        return '' if element is None else element.text.strip()

    @staticmethod
    def loadMore() -> list[Job]:
        IndeedScrapper.currentUrl = IndeedScrapper.nextUrl
        return IndeedScrapper.scrape()
