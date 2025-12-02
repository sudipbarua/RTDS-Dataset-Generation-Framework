import random
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from parsel import Selector
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class Browser:
    def __init__(self, search_txt="hacking"):
        self.fb_user = 'tnikola230@gmail.com'
        self.fb_pass = 'tucKN2022'
        self.fb_contact_list = ['sudip', 'Nik Tes']
        self.search_txt = search_txt
        # the below web elements tend to change from time-to-time. So we declare them here for better manageability
        self.yt_consent_xpath = '/html/body/ytd-app/ytd-consent-bump-v2-lightbox/tp-yt-paper-dialog/div[4]/div[2]/div[6]/div[1]/ytd-button-renderer[2]/yt-button-shape/button/yt-touch-feedback-shape/div/div[2]'
        self.yt_vdo_xpath = '//*[@id="video-title"]/yt-formatted-string'
        # self.yt_ad_button = '//*[@id="skip-button:5"]/span/button'
        self.yt_ad_button = '/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[1]/div[2]/div/div/ytd-player/div/div/div[17]/div/div[3]/div/div[2]/span/button'
        self.fb_consent_xpath = '/html/body/div[3]/div[2]/div/div/div/div/div[4]/button[2]' 
        self.msngr_consent_xpath = '/html/body/div[2]/div[2]/div/div/div/div/div[3]/button[2]'
        self.fb_loginButton_xpath = '/html/body/div[1]/div[1]/div[1]/div/div/div/div[2]/div/div[1]/form/div[2]/button'

    def driver_init(self):
        # initiate the driver. n.b.: for windows machines not no execution path is required
        options = webdriver.ChromeOptions()
        # options.add_argument("start-maximized")
        options.add_argument("--disable-notifications")
        options.add_argument("disable-infobars")
        options.add_argument("--disable-extensions")
        self.driver = webdriver.Chrome(chrome_options=options, executable_path="/home/sudip/rtds_project/chromedriver")

    def auto_scroll(self, scroll_pause):
        # Get scroll height
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        # scroll the page 10 time
        for i in range(5):
            # Scroll down to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Wait to load page
            time.sleep(scroll_pause)
            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def auto_messenger(self):
        self.driver_init()
        self.driver.get('https://www.messenger.com/')
        # consent
        self.driver.find_element(By.XPATH, self.msngr_consent_xpath).click()
        login = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="email"]')))
        login.send_keys(self.fb_user)
        login = self.driver.find_element(By.XPATH, '//*[@id="pass"]')
        login.send_keys(self.fb_pass)
        login.send_keys(Keys.ENTER)
        ridx = random.randint(0, len(self.fb_contact_list) - 1)  # get a random name from the contact list
        # get search box and send name
        sr = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@type="search"]')))
        sr.send_keys(self.fb_contact_list[ridx])
        # click/select the first name from the list
        first_name = '/html/body/div[1]/div/div/div/div[2]/div/div/div/div[2]/div/div/div[1]/div[1]/div/div[1]/ul/li[1]/ul/li[2]/div/a/div'
        ac = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, first_name)))
        ac.click()
        # send message, gif, file (Not implemented)
        print(self.driver.title)
        self.driver.close()  # only closes the corresponding window

    def browse_ddgo(self):
        self.driver_init()
        self.driver.get('https://duckduckgo.com/')
        sr = self.driver.find_element(By.NAME, 'q')
        sr.send_keys(self.search_txt)
        sr.send_keys(Keys.ENTER)
        links = []
        elements = self.driver.find_elements(By.CLASS_NAME, 'eVNpHGjtxRBq_gLOfGDr')
        for element in elements:
            links.append(element.get_attribute('href'))

        for link in links:
            self.driver.get(link)
            time.sleep(10)
        print(self.driver.title)
        self.driver.close()  # only closes the corresponding window

    def browse_hotels(self, place='Hamburg', n_results=5):
        self.driver_init()
        self.driver.get('https://www.booking.com/')
        search = self.driver.find_element(By.NAME, 'ss')
        search.send_keys(place)
        search.send_keys(Keys.ENTER)
        try:
            # get the name of the hotels and corresponding links
            elements = self.driver.find_elements(by="xpath", value="//a[contains(@class, 'e13098a59f')]")
            # from the names and links list only list the urls
            links = list(map(lambda hotel: hotel.get_attribute("href"), elements))
            # visit the hotel links
            for i in range(0, n_results):
                if i == n_results:
                    break
                self.driver.get(links[i])
                time.sleep(10)
        except Exception as e:
            print(e)
        self.driver.close()  # only closes the corresponding window

    def browse_and_scroll(self, link, pause_time=10):
        self.driver_init()
        self.driver.get(link)
        self.auto_scroll(scroll_pause=pause_time)
        print(self.driver.title)
        self.driver.close()  # only closes the corresponding window

    def browse_linkedin(self, n_links=5):
        # n_links is the number job links to be visited
        self.driver_init()
        self.driver.get('https://www.linkedin.com/')
        self.driver.find_element(By.XPATH, '/html/body/nav/div/a[2]').click()  # click on the sign in button
        time.sleep(3)
        login = self.driver.find_element(By.XPATH, '//*[@id="username"]')
        login.send_keys(self.fb_user)
        login = self.driver.find_element(By.XPATH, '//*[@id="password"]')
        login.send_keys(self.fb_pass)
        login.send_keys(Keys.ENTER)
        # Skip verify option1:
        # lambda-1: if skip mobile number verification is required
        # interim_steps = [lambda: self.driver.find_element(By.XPATH, '//*[@id="ember455"]/button').click()]  # add more if required
        # for step in interim_steps:
        #     try:
        #         step()
        #     except Exception as e:
        #         print(e)
        #         pass
        # Skip mobile number verification option2:
        try:
            self.driver.find_element(By.XPATH, '//*[@id="ember455"]/button').click()
        except:
            print(f'Scrip verification was not required:')
        time.sleep(5)
        # Jobs page
        self.driver.get('https://www.linkedin.com/jobs/')
        time.sleep(3)
        # go to search page directly
        self.driver.get('https://www.linkedin.com/jobs/search/?currentJobId=3364206951&geoId=101282230&keywords=Cybersecurity%20Engineer&location=Germany&refresh=true')
        time.sleep(1)
        # Get all links for these offers
        links = []
        # Navigate 3 pages
        print('Links are being collected now.')
        try:
            for page in range(2, 5):
                time.sleep(2)
                jobs_list = self.driver.find_elements(By.CSS_SELECTOR, '.jobs-search-results__list-item')

                for job in jobs_list:
                    all_links = job.find_elements(By.TAG_NAME, 'a')
                    for a in all_links:
                        if str(a.get_attribute('href')).startswith(
                                "https://www.linkedin.com/jobs/view") and a.get_attribute('href') not in links:
                            links.append(a.get_attribute('href'))
                        else:
                            pass
                    # scroll down for each job element
                    self.driver.execute_script("arguments[0].scrollIntoView();", job)

                print(f'Collecting the links in the page: {page - 1}')
                # go to next page:
                self.driver.find_element(By.XPATH, f"//button[@aria-label='Page {page}']").click()
                time.sleep(3)
        except Exception as e:
            print(e)
            pass
        # visit 5 job links
        for i in range(n_links):
            rand_idx = random.randint(0, len(links) - 1)
            self.driver.get(links[rand_idx])
            time.sleep(5)
        print(self.driver.title)
        self.driver.close()  # only closes the corresponding window

    def browse_facebook(self):
        self.driver_init()
        self.driver.get('https://www.facebook.com/')
        try:
            self.driver.find_element(By.XPATH, self.fb_consent_xpath).click()  # click fb consent button
            self.driver.find_element(By.XPATH, '//*[@id="email"]').send_keys(self.fb_user)
            self.driver.find_element(By.XPATH, '//*[@id="pass"]').send_keys(self.fb_pass)
            self.driver.find_element(By.XPATH, self.fb_loginButton_xpath).click()  # click login button
            time.sleep(5)  # provide sufficient time to load the page
            search_box = self.driver.find_element(By.XPATH, "//input[@type='search']")
            search_box.send_keys("Science")
            search_box.send_keys(Keys.ENTER)
            self.driver.get('https://www.facebook.com/ScienceMagazine')  # load this page
            time.sleep(5)  # provide sufficient time to load the page
            # scroll down the loaded page
            self.auto_scroll(scroll_pause=10)
        except Exception as e:
            print(e)
        print(self.driver.title)
        self.driver.close()  # only closes the corresponding window

    def browse_amazon(self, amz_search_txt='Laptop'):
        self.driver_init()
        product_link = []
        self.driver.get('https://www.amazon.de/')
        try:
            # search product
            search = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'twotabsearchtextbox')))
            search.send_keys(amz_search_txt)
            search.send_keys(Keys.ENTER)
            # locate the search results
            items = WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "s-result-item s-asin")]')))
            for item in items:
                # extract the product link
                link = item.find_element(By.XPATH, './/a[@class="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"]').get_attribute("href")
                product_link.append(link)
            # visit product pages by url for 5s
            for i in range(5):
                ridx = random.randint(0, len(product_link)-1)
                self.driver.get(product_link[ridx])
                time.sleep(5)
        except Exception as e:
            print(e)
        self.driver.close()  # only closes the corresponding window

    def browse_google(self):
        self.driver_init()
        self.driver.get('https://www.google.com/')
        try:
            self.driver.find_element(By.XPATH, '//*[@id="L2AGLb"]/div').click()  # click google consent
            # search with keyword or text
            search = self.driver.find_element(By.NAME, "q")
            search.send_keys(self.search_txt)  # input text in search bar
            search.send_keys(Keys.ENTER)
            time.sleep(5)
            # locate URL for organic results element from html script by _xpath
            organic_result = self.driver.find_elements(By.XPATH, '//*[@class="yuRUbf"]/a[@href]')
            # get all URL and store it in variable "url_list" list using for loop
            url_list = []
            for organic_url in organic_result:
                url_list.append(organic_url.get_attribute("href"))
            # visit 5 the sites listed are in the url list and wait 10s
            for i in range(5):
                ridx = random.randint(0, len(url_list)-1)
                self.driver.get(url_list[ridx])
                time.sleep(5)
        except Exception as e:
            print(f"Taking too long to load the page. Error: {e}")
        print(self.driver.title)
        self.driver.close()  # only closes the corresponding window

    def browse_youtube(self, yt_play_time=60):
        self.driver_init()
        self.driver.get('https://www.youtube.com')
        try:
            time.sleep(5)
            self.driver.find_element(By.XPATH, self.yt_consent_xpath).click()
            # sleep 5s since YouTube takes time to reload after giving the consent
            time.sleep(5)
            self.driver.find_element(By.NAME, "search_query").send_keys(self.search_txt)  # input text in search bar
            self.driver.find_element(By.CSS_SELECTOR, "#search-icon-legacy.ytd-searchbox").click()  # click search button
            # find element with explicit wait
            play = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, self.yt_vdo_xpath)))
            play.click()
            time.sleep(10)
            self.driver.find_element(By.XPATH, self.yt_ad_button).click()
        except Exception as e:
            print(f"Taking too long to load the page. Error: {e}")
        time.sleep(yt_play_time)
        self.driver.close()  # only closes the corresponding window
    