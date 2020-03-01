from profiles.scraper import LinkedInScraper
import sys
import boto3
from constants import *

# Need selenium installation
linkedin_scraper = None

#Initialize boto3 client
s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)

# if any(command in sys.argv for command in ['runserver']):
#     linkedin_scraper = LinkedInScraper()
#     linkedin_scraper.login()

# else:
#     linkedin_scraper = None
