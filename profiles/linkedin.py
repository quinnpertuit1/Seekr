from .scraper import LinkedInScraper
import time
import urllib.request
import json
#from conf import EMAIL, PASSWORD
from profiles.models import Profile, Education, Experience
from global_variables import linkedin_scraper

class LinkedIn:
    def __init__(self):
        self.scraper = linkedin_scraper

    # Checks database for matches, and scrapes more if not enough
    def get_profiles(self, company, title, num_profiles):
        # first check in the database to see there are enough num_profiles
        # then call get_linkedin_urls_google_search, and then pass those urls to the scraper
        # and then store in the db
        profiles = []
        exclude_urls = []
        profiles += [p for p in Profile.objects.filter(experience__company__contains=company, 
                        experience__title__contains=title)]
        exclude_urls += [p.profile_url for p in Profile.objects.filter(experience__company__contains=company, 
                        experience__title__contains=title)]

        linkedin_scraper= LinkedInScraper()
        linkedin_scraper.login()

        while len(profiles) < num_profiles:
            linkedin_scraper.get_profiles(company, title, (num_profiles - len(profiles)), exclude_urls)
            # technically the missing profiles that we fetched from scraper would be added to the DB by now
            profiles = []
            profiles += [p for p in Profile.objects.filter(experience__company__contains=company, 
                        experience__title__contains=title)]
            exclude_urls += [p.profile_url for p in Profile.objects.filter(experience__company__contains=company, 
                        experience__title__contains=title)]
                        
        return profiles # returning a list of Query objects for now 

    # LinkedIn Search is restricted to certain amount of people,
    # Can use google to search instead.
    def get_linkedin_urls_google_search(self, company, title):
        url = "https://www.googleapis.com/customsearch/v1?key=&cx=&q=" + company + title

        searchResult = urllib.request.urlopen(url)
        data = searchResult.read()
        encodedData = searchResult.info().get_content_charset('utf-8')
        resultingData = json.loads(data.decode(encodedData))

        urlList = []

        for results in resultingData["items"]:
            urlList.append(results["link"])

        return urlList
