from selenium import webdriver
from selenium.common.exceptions import (
    TimeoutException, StaleElementReferenceException, 
    WebDriverException, NoSuchElementException
)
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
import logging
import time
import os
from datetime import date, datetime
from .models import Profile, Experience, Education
import re
from utils.utils import random_sleep
from .search import GoogleSearch

logger = logging.getLogger('app')

POLL_FREQUENCY = 0.1
WAIT_TIMEOUT = 15
WINDOW_SIZE = 800
LINKEDIN_EMAIL = os.environ['LINKEDIN_EMAIL']
LINKEDIN_PASSWORD = os.environ['LINKEDIN_PASSWORD']

class SeleniumScraper:
    xpaths = {}
    def __init__(self, headless=True):
        if headless:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            driver = webdriver.Chrome(chrome_options=options)
        else:
            driver = webdriver.Chrome()

        self.d = driver

    def visit(self, url):
        logger.info("Visiting {}".format(url))
        try:
            self.d.get(url)
        except:
            logger.error("Driver get error.")

    def quit(self):
        self.d.quit()

    def element_get_by_xpath_or_none(self, el, xpath_key, logs=True):
        """
        Get a web element through the xpath string passed.
        If a TimeoutException is raised the else_case is called and None
        is returned.
        :param driver: Selenium Webdriver to use.
        :param xpath: String containing the xpath.
        :param wait_timeout: optional amounts of seconds before
        TimeoutException is raised, default WAIT_TIMEOUT is used otherwise.
        :param logs: optional, prints a status message to stdout if an
        exception occures.
        :return: The web element or None if nothing found.
        """
        try:
            return el.find_element_by_xpath(self.xpaths[xpath_key])
        except (TimeoutException, StaleElementReferenceException,
                WebDriverException, NoSuchElementException) as e:
            if logs:
                logger.warning(f"XPATH: {xpath_key} ")
            return None

    def element_get_multiple_by_xpath_or_none(self, el, xpath_key, logs=True):
        """
        Get a web element through the xpath string passed.
        If a TimeoutException is raised the else_case is called and None
        is returned.
        :param driver: Selenium Webdriver to use.
        :param xpath: String containing the xpath.
        :param wait_timeout: optional amounts of seconds before
        TimeoutException is raised, default WAIT_TIMEOUT is used otherwise.
        :param logs: optional, prints a status message to stdout if an
        exception occures.
        :return: The web element or None if nothing found.
        """
        try:
            return el.find_elements_by_xpath(self.xpaths[xpath_key])
        except (TimeoutException, StaleElementReferenceException,
                WebDriverException, NoSuchElementException) as e:
            if logs:
                logger.warning(f"XPATH: {xpath_key} ")
            return None

    def scroll_to_bottom(self, body_height):
        top = 0
        while top < body_height:
            top += WINDOW_SIZE * 2 // 3
            scroll = "window.scrollTo(0, " + str(top) + ")"
            self.d.execute_script(scroll)
            time.sleep(0.1)

    def element_get_text_by_xpath_or_none(self, el, xpath_key, logs=True):
        element = self.element_get_by_xpath_or_none(el, xpath_key, logs)
        if not element:
            return None
        else:
            return element.text

    def element_get_text_by_xpath_or_empty_string(self, el, xpath_key, logs=True):
        element = self.element_get_by_xpath_or_none(el, xpath_key, logs)
        if not element:
            return ""
        else:
            return element.text

    def wait_get_by_xpath(self, xpath_key):
        """
        Get a web element through the xpath passed by performing a Wait on it.
        :param xpath: xpath to use.
        :return: The web element.
        """
        return WebDriverWait(self.d, WAIT_TIMEOUT, poll_frequency=POLL_FREQUENCY).until(
            ec.presence_of_element_located(
                (By.XPATH, self.xpaths[xpath_key])
            ))

    def get_by_xpath(self, xpath_key):
        """
        Get a web element through the xpath
        :param xpath_key: xpath_key to use to access the xpath dictionary
        :return: The web element.
        """
        return self.d.find_element_by_xpath(self.xpaths[xpath_key])

    def get_by_xpath_or_none(self, xpath_key, wait=False, logs=True):
        """
        Get a web element through the xpath string passed.
        If a TimeoutException is raised the else_case is called and None is returned.
        :param xpath: String containing the xpath.
        :param wait_timeout: optional amounts of seconds before TimeoutException is raised, default WAIT_TIMEOUT is used otherwise.
        :param logs: optional, prints a status message to stdout if an exception occures.
        :return: The web element or None if nothing found.
        """
        try:
            if wait:
                return self.wait_get_by_xpath(xpath_key)
            else:
                return self.get_by_xpath(xpath_key)

        except (TimeoutException, StaleElementReferenceException, WebDriverException, NoSuchElementException) as e:
            if logs:
                logger.warning(f"Couldn't find XPATH: {xpath_key} ")
            return None

    def get_by_xpath_text_or_none(self, xpath_key, wait=False, logs=True):
        element = self.get_by_xpath_or_none(xpath_key, wait, logs)
        if not element:
            return None
        else:
            return element.text

    def get_multiple_by_xpath_or_none(self, xpath_key, wait=False, logs=True):
        """
        Get a web element through the xpath string passed.
        If a TimeoutException is raised the else_case is called and None is returned.
        :param xpath: String containing the xpath.
        :param wait_timeout: optional amounts of seconds before TimeoutException is raised, default WAIT_TIMEOUT is used otherwise.
        :param logs: optional, prints a status message to stdout if an exception occures.
        :return: The web element or None if nothing found.
        """
        if wait:
            try:
                # Polling call, returns when something is found
                self.wait_get_by_xpath(xpath_key)
            except (TimeoutException, StaleElementReferenceException, WebDriverException) as e:
                if logs:
                    logger.warning(f"Couldn't find XPATH: {xpath_key} ")
                return None

        try:
            return self.d.find_elements_by_xpath(self.xpaths[xpath_key])
        except:
            if logs:
                if wait:
                    logger.warning(f"Found XPATH: {xpath_key}, couldn't find all elements.")
                else:
                    logger.warning(f"Couldn't find XPATH: {xpath_key} ")
            return None

    def get_multiple_by_xpath_text_or_none(self, xpath_key, wait=False, logs=True):
        element = self.get_multiple_by_xpath_or_none(xpath_key, wait, logs)
        if not element:
            return None
        else:
            return [element.text for element in elements]

class LinkedInScraper(SeleniumScraper):
    urls = {'LINKEDIN_LOGIN_URL': 'https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin',
            'BASE_LINKEDIN': 'https://www.linkedin.com/',
            'LINKEDIN_PEOPLE_SEARCH': 'https://www.linkedin.com/search/results/people/?keywords={}&page={}',
            'SIGN_IN': 'https://www.linkedin.com/uas/login?session_redirect=https%3A%2F%2Fwww%2Elinkedin%2Ecom%2Fin%2Fjoyliu3&amp;trk=public_auth-wall_profile'}
    
    xpaths = {
        'USERNAME': '//*[@id="username"]',
        'PASSWORD': '//*[@id="password"]',
        'SEARCH_PEOPLE': '//*[@data-control-name="search_srp_result"]',
        'SEARCH_RESULT_ITEM': '//li[@class="search-result search-result__occluded-item ember-view"]',
        'PROFILE_NAME': '//*[@class="inline t-24 t-black t-normal break-words"]',
        'LOCATION': '//li[@class="t-16 t-black t-normal inline-block"]',
        'EXPERIENCES': '//*[@class="pv-profile-section__card-item-v2 pv-profile-section pv-position-entity ember-view"]',
        'MULTI_ROLES_LI': './/li[@class="pv-entity__position-group-role-item"]',
        'MULTI_ROLES_LI_FADING': './/li[@class="pv-entity__position-group-role-item-fading-timeline"]',
        'TITLE': './/h3[@class="t-16 t-black t-bold"]',
        'COMPANY': './/p[@class="pv-entity__secondary-title t-14 t-black t-normal"]',
        'COMPANY_MULTI_EXPERIENCES': './/h3[@class="t-16 t-black t-bold"]',
        'TITLE_MULTI_EXPERIENCES': './/h3[@class="t-14 t-black t-bold"]',
        'DATE_RANGE': './/h4[@class="pv-entity__date-range t-14 t-black--light t-normal"]',
        'JOB_DESCRIPTION': './/p[@class="pv-entity__description t-14 t-black t-normal inline-show-more-text inline-show-more-text--is-collapsed ember-view"]',
        'EDUCATION_SINGLE': '//li[@class="pv-profile-section__list-item pv-education-entity pv-profile-section__card-item ember-view"]',
        'SCHOOL': './/h3[@class="pv-entity__school-name t-16 t-black t-bold"]',
        'DEGREE': './/p[@class="pv-entity__secondary-title pv-entity__degree-name t-14 t-black t-normal"]',
        'FIELD_OF_STUDY': './/p[@class="pv-entity__secondary-title pv-entity__fos t-14 t-black t-normal"]',
        'GRADE': './/p[@class="pv-entity__secondary-title pv-entity__grade t-14 t-black t-normal"]',
        'SCHOOL_DATE_RANGE': './/p[@class="pv-entity__dates t-14 t-black--light t-normal"]',
        'EDUCATION_DESCRIPTION': './/p[@class="pv-entity__description t-14 t-normal mt4"]',
        'SHOW_MORE': './/button[@class="pv-profile-section__card-action-bar pv-skills-section__additional-skills artdeco-container-card-action-bar artdeco-button artdeco-button--tertiary artdeco-button--3 artdeco-button--fluid"]',
        'FETCH_PROFILE_FROM_SEARCH': '//a[contains(@class, "search-result__result-link ember-view")]',
        'PIN_VERIFY': '//*[@id="input__email_verification_pin"]',
    }

    def login(self):
        self.visit(self.urls['LINKEDIN_LOGIN_URL'])

        logger.info("Looking for Email and Password text boxes...")
        username = self.get_by_xpath_or_none('USERNAME', wait=True)
        if username:
            username.send_keys(LINKEDIN_EMAIL)
        
        password = self.get_by_xpath_or_none('PASSWORD', wait=False)
        if password:
            password.send_keys(LINKEDIN_PASSWORD + '\n')
        logger.info("Found input boxes, waiting for authentication...")

    def pin_verify(self, pin):
        pin_box = self.get_by_xpath_or_none('PIN_VERIFY', wait=True)
        pin_box.send_keys(pin + '\n')

    def get_profile_urls(self, company, role, page_num, exclude_usernames=[]):
        try:
            logger.info("Looking for {} roles at {} on the {} page...".format(
                role, company, page_num))
            logger.info("Excluded usernames: {}".format(' '.join(exclude_usernames)))

            query = '%20'.join(company.split()) + '%20' + '%20'.join(role.split())
            url = self.urls['LINKEDIN_PEOPLE_SEARCH'].format(query, page_num)

            self.visit(url)
            random_sleep(1, 0.3)
            self.scroll_to_bottom(800)

            new_profile_urls = [p.get_attribute('href')
                for p in self.get_multiple_by_xpath_or_none('FETCH_PROFILE_FROM_SEARCH')]
            new_profile_urls = list(set(new_profile_urls))

            if not new_profile_urls:
                logger.info("Can't find anymore profiles, stopping iteration.")
                raise StopIteration()
            
            filtered_profile_urls = [p for p in new_profile_urls
                if Profile.url_to_username(p) not in exclude_usernames]
            logger.info("Found {} profiles on this page, filtered to {} profiles".format(
                len(new_profile_urls), len(filtered_profile_urls)))
            return filtered_profile_urls
        except StopIteration as e:
            raise e
        except:
            self.login()
            logger.exception("Error inn getting urls")

    def get_profile_urls_google(self, company, role, page_num, exclude_usernames=[]):
        try:
            logger.info("Looking for {} roles at {} on the {} page...".format(
                role, company, page_num))
            logger.info("Excluded usernames: {}".format(' '.join(exclude_usernames)))
            query = '%20'.join(company.split()) + '%20' + '%20'.join(role.split())

            profiles = GoogleSearch.get_linkedin_profiles_simple(query, page_num)
            
            new_profile_urls = [p['profile_url'] for p in profiles]
            new_profile_urls = list(set(new_profile_urls))

            if not new_profile_urls:
                logger.info("Can't find anymore profiles, stopping iteration.")
                raise StopIteration()
            
            filtered_profile_urls = [p for p in new_profile_urls
                if Profile.url_to_username(p) not in exclude_usernames]
            logger.info("Found {} profiles on this page, filtered to {} profiles".format(
                len(new_profile_urls), len(filtered_profile_urls)))
            return filtered_profile_urls
            
        except StopIteration as e:
            raise e
        except:
            self.login()
            logger.exception("Error inn getting urls")


    def get_profiles(self, company, role, num_profiles, exclude_usernames=[]): 
        """
        Get the required number of profiles.
        This is done by multiple helper functions above.
        :param company: Company name we're searching.
        :param role: Role we're searching for.
        :param num_profiles: Required number of profiles to fetch and store.
        :param exclude_usernames: List of profile to exclude from fetching.
        """
        page_num = 1
        num_collected = 0

        profiles = []

        while num_collected < num_profiles and page_num < 10:
            # LinkedIn Search
            try:
                profile_urls = self.get_profile_urls_google(company, 
                    role, page_num, exclude_usernames)
                
            except:
                break;
            
            for profile_url in profile_urls:
                profile = self.get_profile_by_url(profile_url, company, role)
                if profile:
                    profiles.append(profile)
                    num_collected += 1
                    if num_collected >= num_profiles:
                        return profiles
                else:
                    logger.info("She/He doesn't appear to worked as a {} at {}".format(
                        role, company))

                random_sleep(1, 0.3)
            page_num += 1

        return profiles

    def get_profile_by_url(self, profile_url, company="", role=""): 
        """
        Scrape basic information of a profile through the given profile URL and store them in Profiles DB.
        This is done by login into LinkedIn and going to the given profile URL.
        If the profile doesn't have experience or education fields we need, then do not store into DB.
        :param profile_url: Person's profile URL that we will be extracting information from.
        :return: True if we have stored the profile into DB, False if we did not store.
        """ 
        username = Profile.url_to_username(profile_url)

        p = Profile.objects.filter(pk=username).first()
        if p:
            logger.info("A profile with username {} exists in the database.".format(
                username))
            return p

        self.visit(profile_url)
        try:
            self.scroll_to_bottom(1500)
            name = self.get_by_xpath_text_or_none('PROFILE_NAME', wait=True)
            location = self.get_by_xpath_text_or_none('LOCATION', wait=False)
            experiences = self.parse_profile_experiences(company, role)

            if experiences is None:
                logger.info("{} has no experience.".format(name))
                return False

            educations = self.parse_profile_education()
            gpa = None

            profile = Profile.objects.create(name=name, location=location, username=username)
            logger.info("Successfully created {}'s profile".format(username))
            
            education_list = []
            for education in educations:
                if education['grade'] is not None:
                    gpa = LinkedInScraper.extract_gpa(education['grade'])
                
                is_education_current = False
                if education["end_date"] >= datetime.today():
                    is_education_current = True

                e = Education(
                    school_name=education['institution'],
                    degree=education['degree'],
                    field_of_study = education['field_of_study'],
                    description=education['description'],
                    gpa=gpa,
                    start_date=education["start_date"],
                    end_date=education["end_date"],
                    is_current=is_education_current,
                    profile=profile,
                )
                education_list.append(e)
                logger.info("Found education  {}".format(e))

            Education.objects.bulk_create(education_list)

            experience_list = []
            for experience in experiences:
                is_experience_current = True
                # NOTE: LinkedIn requires users to input experience date range
                experience_date_range = experience["dates"]
                experience_start_date = datetime.now().strftime("%Y-%m-%d")
                experience_end_date = datetime.now().strftime("%Y-%m-%d")

                experience_start_date_month = experience_date_range.split('\n')[1].split(' ')[0]
                    
                if str.isdigit(experience_start_date_month): # NOTE: if user decides to not put a month for start date
                    experience_start_date_year = experience_start_date_month
                    experience_start_date = datetime.strptime("Jan" + " 01 " + experience_start_date_year, '%b %d %Y')
                else:
                    experience_start_date_year = experience_date_range.split('\n')[1].split(' ')[1]
                    experience_start_date = datetime.strptime(experience_start_date_month + " 01 " + experience_start_date_year, '%b %d %Y')

                try: 
                    experience_end_date_month = experience_date_range.split('\n')[1].split(' ')[2]
                except IndexError: # NOTE: when user only put year for both start and end date
                    experience_end_date = datetime.strptime("Dec" + " 01 " + experience_start_date_year, '%b %d %Y')
                else:
                    try:
                        experience_end_date_month = experience_date_range.split('\n')[1].split(' ')[3]
                    except IndexError: # NOTE: this means that user either put present or just put a year for end date
                        experience_end_date_month = experience_date_range.split('\n')[1].split(' ')[2]
                    else: 
                        experience_end_date_month = experience_date_range.split('\n')[1].split(' ')[3]

                    if experience_end_date_month != "Present":
                        is_experience_current = False
                        if str.isdigit(experience_end_date_month): # NOTE: if user decides to not put a month for end date
                            experience_end_date_year = experience_end_date_month
                            experience_end_date = datetime.strptime("Dec" + " 01 " + experience_end_date_year, '%b %d %Y')

                        else:
                            experience_end_date_year = experience_date_range.split('\n')[1].split(' ')[4]
                            experience_end_date = datetime.strptime(experience_end_date_month + " 01 " + experience_end_date_year, '%b %d %Y')
                
                e = Experience(
                    company=experience["company"],
                    description=experience["description"],
                    title = experience["title"],
                    start_date=experience_start_date,
                    end_date=experience_end_date,
                    is_current=is_experience_current,
                    profile=profile,
                )
                experience_list.append(e)
                logger.info("Found experience {}".format(e))

                
            Experience.objects.bulk_create(experience_list)

            return profile
        except:
            self.login()
            logger.exception("Problem getting profile.")

    def parse_profile_experiences(self, company, role):
        """
        Scrape all the experiences and their corresponding detail about each experience on this profile page.
        If the profile doesn't have any experience, then return None.
        :return: List of dictionaries containing information about each experience. Return None if no experience.
        """
        experiences = []
        exps = self.get_multiple_by_xpath_or_none('EXPERIENCES')

        if not exps:
            return None

        for exp in exps:
            # Multiple roles in 1 company
            mult_roles_li = self.element_get_multiple_by_xpath_or_none(exp, 'MULTI_ROLES_LI')
            if not mult_roles_li:
                mult_roles_li = self.element_get_multiple_by_xpath_or_none(exp, 'MULTI_ROLES_LI_FADING')
                
            if mult_roles_li:
                company = self.element_get_text_by_xpath_or_empty_string(exp, 'COMPANY_MULTI_EXPERIENCES').split('\n')[1]
                for role in mult_roles_li:
                    temp = {
                        'company': company,
                        'title': self.element_get_text_by_xpath_or_empty_string(role,
                            'TITLE_MULTI_EXPERIENCES').split('\n')[1],
                        'dates': self.element_get_text_by_xpath_or_empty_string(role, 'DATE_RANGE'),
                        'description': self.element_get_text_by_xpath_or_empty_string(exp, 'JOB_DESCRIPTION')
                    }
                    experiences.append(temp)
            else:
                temp = {}
                temp['dates'] = self.element_get_text_by_xpath_or_empty_string(exp, 'DATE_RANGE')
                temp['title'] = self.element_get_text_by_xpath_or_empty_string(exp, 'TITLE')
                temp['company'] = self.element_get_text_by_xpath_or_empty_string(exp, 'COMPANY')
                temp['description'] = self.element_get_text_by_xpath_or_empty_string(exp, 'JOB_DESCRIPTION')
                
                if temp['dates'] and temp['title'] and temp['company']:
                    experiences.append(temp)

        return experiences

    def extract_gpa(grade):
        """
        Manipulate the string form of extracted grade of education into a relative gpa number
        :return: Float number indicating the relative gpa. None if no numerical number can be found in grade.
        """
        gpas = re.findall('[0-4]\.[0-9]?[0-9]?', grade)
        if not gpas:
            return None

        gpas = map(lambda x: float(x), gpas)
        return min(gpas)

    def parse_profile_education(self):
        """
        Scrape all the education and corresponding details about each education on this profile page.
        If the profile doesn't have any education, or if the most recent education is missing school name, date range, or field of study, then return None.
        For any subsequent education that occurred earlier than the most recent education, do not add in the returning list if it's missing school name, date range, or field of study.
        :return: List of dictionaries containing information about each education. Return [] if above condition does not satisfy.
        """
        educations = []
        get_educations = self.get_multiple_by_xpath_or_none("EDUCATION_SINGLE")

        iteration = 0
        for education in get_educations:
            temp = {}
            temp["institution"] = self.element_get_text_by_xpath_or_none(
                    education, "SCHOOL") if self.element_get_text_by_xpath_or_none(education, "SCHOOL") is not None else ""
            temp["field_of_study"] = self.element_get_text_by_xpath_or_none(
                    education, "FIELD_OF_STUDY").split('\n')[1] if self.element_get_text_by_xpath_or_none(education, "FIELD_OF_STUDY") is not None else "" 
            degree = self.element_get_text_by_xpath_or_none(
                    education, "DEGREE").split('\n')[1] if self.element_get_text_by_xpath_or_none(education, "DEGREE") is not None else ""
            
            # degree = degree.lower()

            # if "bachelor" in degree or "bcs" in degree or "BSC" in degree :
            #     degree = "Bachelor"
            # elif "master" in degree:
            #     degree = "Master"
            # elif "phd" in degree:
            #     degree = "PhD"
            # else:
            #     degree = "Othe

            temp["degree"] = degree
            temp["grade"] = self.element_get_text_by_xpath_or_none(
                    education, "GRADE").split('\n')[1] if self.element_get_text_by_xpath_or_none(education, "GRADE") is not None else ""
            
            start_date = ""
            end_date = ""
            school_date_range = self.element_get_text_by_xpath_or_none(
                    education, "SCHOOL_DATE_RANGE") if self.element_get_text_by_xpath_or_none(education, "SCHOOL_DATE_RANGE") is not None else ""
            if school_date_range != "":
                start_date = datetime(int(school_date_range.split('\n')[1].split(' ')[0]), 9, 1)
                try:
                    int(school_date_range.split('\n')[1].split(' ')[2])
                except IndexError:
                    school_date_range = ""
                else:
                    end_date = datetime(int(school_date_range.split('\n')[1].split(' ')[2]), 5, 1)
                
            temp["start_date"] = start_date
            temp["end_date"] = end_date

            temp["description"] = self.element_get_text_by_xpath_or_none(
                    education, "EDUCATION_DESCRIPTION") if self.element_get_text_by_xpath_or_none(education, "EDUCATION_DESCRIPTION") is not None else ""

            if iteration == 0 and (temp["institution"] == ""
                    or temp["field_of_study"] == "" or school_date_range == ""):
                return []
            elif iteration>=0 and (temp["institution"] != ""
                    and temp["field_of_study"] != "" and school_date_range != ""):
                educations.append(temp)
            iteration+=1

        return educations