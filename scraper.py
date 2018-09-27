#!/usr/bin/env python

import re
import urlparse

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from time import sleep

link = 'https://l3com.taleo.net/careersection/l3_ext_us/jobsearch.ftl'

class TaleoJobScraper(object):
    def __init__(self):
        self.driver = webdriver.PhantomJS()
        self.driver.set_window_size(1120, 550)
        self.wait = WebDriverWait(self.driver, 10)

    def scrape_job_links(self):
        self.driver.get(link)

        r = re.compile(r'\d+ - \d+ of \d+')
        f = lambda d: re.search(r, d.find_element_by_id('currentPageInfo').text)

        self.wait.until(f)

        m = f(self.driver)
        t = m.group(0)

        jobs = []
        pageno = 2

        while True:
            print 'Scraping page %d' % (pageno - 1)

            s = BeautifulSoup(self.driver.page_source)
            h = re.compile(r'jobdetail\.ftl\?job=\d+')

            for a in s.findAll('a', href=h):
                tr = a.findParent('tr')
                td = tr.findAll('td')

                job = {}
                job['title'] = a.text
                job['url'] = urlparse.urljoin(link, a['href'])
                job['location'] = td[1].text
                jobs.append(job)

            next_page_elem = self.driver.find_element_by_id('next')
            next_page_link = s.find('a', text='%d' % pageno)

            if next_page_link:
                next_page_elem.click()

                # Watch for the transition from "1 - 25 of 1106" to "26 - 50 of 1106"
                self.wait.until(lambda d: f(d) and f(d).group(0) != t)

                m = f(self.driver)
                t = m.group(0)

                pageno += 1
            else:
                break

        return jobs

    def scrape_job_descriptions(self, jobs):
        for job in jobs:
            self.driver.get(job['url'])            

            s = BeautifulSoup(self.driver.page_source)
            x = {'class': 'mastercontentpanel3'}
            d = s.find('div', attrs=x)

            if not d:
                continue

            job['desc'] = ' '.join(d.findAll(text=True))
            sleep(.75)

    def scrape(self):
        jobs = self.scrape_job_links()
        for job in jobs:
            print job

        self.driver.quit()

if __name__ == '__main__':
    scraper = TaleoJobScraper()
    scraper.scrape()
