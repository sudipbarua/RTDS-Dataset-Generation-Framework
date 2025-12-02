import sched
import multiprocessing
from threading import Thread
import schedule
import random
import time
import os
import platform
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from skpy import Skype
import yaml
import smtplib
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
import re
import ftplib
import pickle
import socket
import pandas as pd
from datetime import datetime as dt

with open('log_file_path.yml', 'r') as f:
    config_file = yaml.safe_load(f)
log_file_path = config_file['log_paths']['log_file_path']
log_txt_file_path = config_file['log_paths']['log_txt_file_path']

def save_logs(bot_name, action):
    # get the system ip address. Required for host labeling
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('google.com', 80))
    local_ip = s.getsockname()[0]
    s.close()

    # save logs to the local csv file
    result = pd.DataFrame({'time':f'{dt.now()}',
                           'Bot IP address': f'{local_ip}',
                           'Bot name': f'{bot_name}',
                           'Action': f'{action}'}, index=[0])
    result.to_csv(log_file_path, mode='a', index=False, header=False)

class NormalBot:
    def __init__(self, name: str):
        self.name = name
        self.browseList = []  # we add an empty list which later would contain different object, we have one list per category like browsing or email
        self.chatList = []
        self.emailList = []
        self.FTPList = []
        self.actionList = {}
        self.process_list = []
        self.method_list = []

    # ---methods to add obj to each of the lists
    def addBrowse(self, *args):
        for obj in args:
            self.browseList.append(obj)

    def addChat(self, *args):
        for obj in args:
            self.chatList.append(obj)

    def addEmail(self, *args):
        for obj in args:
            self.emailList.append(obj)

    def addFTP(self, *args):
        for obj in args:
            self.FTPList.append(obj)

    def save_bot_obj(self, addr):
        print(f'{dt.now()} The bot obj is saved', file=open(log_txt_file_path, 'a'))
        save_logs(self.name, 'The bot obj is saved')  # saving logs to the csv file

    def return_object_methodList(self, obj):
        # return a list methods for the input object, this list then will be used to choose a random set of methods
        # ----- helper method to retrive all avaialable callable methods of an obj
        # This we use to randomly generate a list of actions (methods) for each object
        return [func for func in dir(obj) if callable(getattr(obj, func)) and (not func.startswith("__"))]

    def get_action_list(self, *args):
        # class list is the one we add to different list in normalBot. e.g. Browsing or email
        # ---This is a method which takes a list of objects category and add different randomly generated method to the list
        # The returned list is just string e.g. 'browseLinkedin.linkedin1': ['__login__', 'scrolUp', 'scrolDown']
        # some of the methods are mandatory for some objects, so we will for sure add them e.g. login for chat or email or linkein
        for input_object_list in args:
            for obj in input_object_list:
                self.actionList[f"{obj.__class__.__name__}.{obj.name}"] = []
                methodList = self.return_object_methodList(obj)  # see how many methods are available for this obj
                if len(methodList) > 1:  # randomly method generation occurs where there is more than one callable methods
                    selectedMethods = random.choices(methodList, k=random.choice(
                        range(1, len(methodList))))  # chose random number of methods (actions)
                else:
                    selectedMethods = methodList  # where there is only one method in the list to be executed
                if 'brows' in obj.__class__.__name__.lower():
                    # forcefully add __driverInit__ at the beginning of the action list
                    self.actionList[f"{obj.__class__.__name__}.{obj.name}"].append('__driverInit__')
                if obj.required_login:  # this way i force the add __login__ method at the first of the action list if class is linkedin or facebook
                    self.actionList[f"{obj.__class__.__name__}.{obj.name}"].append('__login__')
                for action in selectedMethods:
                    self.actionList[f"{obj.__class__.__name__}.{obj.name}"].append(
                        action)  # append each randomly choosen actions in the final action list to be scheduled
                if obj.__class__.__name__ == 'Email':
                    #  I put this in the last bqz we can add various attach or body text methods before sending an email.
                    #  It is mandatory method and should be add at the end of list in email class to sure it will be sent
                    self.actionList[f"{obj.__class__.__name__}.{obj.name}"].append('__send_email__')
                elif 'brows' in obj.__class__.__name__.lower():
                    self.actionList[f"{obj.__class__.__name__}.{obj.name}"].append('__closing__')


    def print_method_list(self, input_list):
        obj_list = []
        for i, object in enumerate(input_list):
            obj_list.append(f"{object.obj.__class__.__name__}.{object.obj.name}.{object.methods}")
        print(f'{dt.now()} ********Randomly generated list of methods for each input objects********', file=open(log_txt_file_path, 'a'))
        save_logs(self.name, f'Randomly generated list of methods for each input objects {obj_list}')  # saving logs to the csv file
        print(f'{dt.now()} {obj_list}', file=open(log_txt_file_path, 'a'))

    def create_combined_method_list(self, *args):  # Wrapper: a function that execute a list of methods
        for input_object_list in args:
            for obj_item in input_object_list:
                for obj, method in self.actionList.items():
                    if obj_item.name == obj.split(".")[1]:
                        # A wrapper class that takes the obj and its method list which is string.
                        # So, we can execute all methods of an object with one function only.
                        # Combining different method into one function and make it process to execute
                        all_methods = execute_methods(obj_item, method)
                        self.method_list.append(all_methods)
        # shuffle the method list to have randomized execution
        random.shuffle(self.method_list)
        self.print_method_list(self.method_list)  # print executable obj and methods in the final list to become process and started

    def start_and_schedule_next_process(self, scheduler, counter, process_list):
        # ---this a helper method for schedule_processes method. make process of methods in the lists and schedule them
        if counter < len(self.method_list):
            p_name = f"{(self.method_list[counter].obj.__class__.__name__)}.{(self.method_list[counter].obj.name)}"  # make a process name w.r.t. class and obj name
            p = multiprocessing.Process(target=self.method_list[counter].execute, name=p_name)  # make a process
            print(f'{dt.now()} +++++++++++++++ Executing Processes: {p_name} Current time: {time.strftime("%H:%M:%S")} +++++++++++++++'
                  , file=open(log_txt_file_path, 'a'))
            save_logs(self.name, f'Executing Processes: {p_name} Current time: {time.strftime("%H:%M:%S")}')  # saving logs to the csv file

            p.start()
            p.join()  # used to ensure that the child process has finished its execution and sequential execution. In our case, we are going to use it for normal-without CD processes. Comment it out during CD 
            process_list.append(p)
            counter += 1
            # scheduler wait for the value in each obj (delay_to_run_next_process), then call start_and_schedule_next_process method again to go for the next method to become process and executed
            scheduler.enter(self.method_list[counter - 1].obj.delay_to_run_next_process, 1,
                            self.start_and_schedule_next_process, (scheduler, counter, process_list))
        else:
            # All processes have been scheduled, do something else or exit the program
            pass

    def schedule_processes(self, warmup_period=10):
        print(f'{dt.now()} ***************************************************************************',
              file=open(log_txt_file_path, 'a'))
        print(f'{dt.now()} Executing bot: {self.name}', file=open(log_txt_file_path, 'a'))
        save_logs(self.name, f'Executing bot: {self.name}')
        # --with help of start_and_schedule_next_process it schedule and run process.
        # At the beginning it waits for a warmup period
        counter = 0
        process_list = []
        # It's not strictly necessary to use a process_list in this case, and the code could still run without it,
        # but it can be useful to have a way to keep track of running processes in more complex scenarios
        # where you might want to manage or monitor the status of multiple processes at once.
        scheduler = sched.scheduler(time.time, time.sleep)
        scheduler.enter(warmup_period, 1, self.start_and_schedule_next_process, (scheduler, counter, process_list))
        scheduler.run()

    def processes_start(self, processes):  # we do not use it now
        for process in processes:
            process.start()

    def processes_wait(self, processes):  # we do not use it now
        for process in processes:
            process.join()

    def process_terminate(self, pid):  # we do not use it now
        for process in self.process_list:
            if process.pid == pid:
                process.terminate()

    def get_process_pid(self, obj):  # we do not use it now
        for process in self.process_list:
            if process.name == f"{type(obj.__self__).__name__}.{obj.__name__}":
                return process.pid

    def show_active_process(self):  # this can be called after staring the process|||| # we do not use it now
        print(f'{dt.now()} Active children: {[p.name for p in multiprocessing.active_children()]}', file=open(log_txt_file_path, 'a'))


class execute_methods:  # Wrapper to execute different methods of  an object
    # Why this class? the problem is that we need a way to execute all methods of an object at once when we pass them to the target of multiprocessing library
    # I any other way, the execution of process was wrong. This way we controll the way we executing different methods of an object
    # This is some how a wrapper to execute all the methods (randomly generated) at once.
    # Before we use lambda :[getattr(browse, item)() for item in method_list] ==> to add methods to a function call lambda. Then we execute only the lambda function as process
    # But it has a logical error, means that one obj with its methods executed in multiple times which was not true. Or the order was not true.
    # This class is like a queue or buffer which takes the obj and the list of its methods to be executed
    def __init__(self, obj, methods):
        self.obj = obj
        self.methods = methods
        self.repeatable_methods = ['clickPlayLink', 'chat_with', 'scrolDown']
        # these are main actionable method that can be repeat for each class. The others like __login__ should be done one time not reapeat
        # excluded doSearch because if it is repeated, same search keyword is passed in the search box after the previous one, making the search results invalid

    def execute(self):
        n_repeatable_methods = sum(1 for m in self.methods if not m.startswith('__'))  # count of the repeatable methods
        for method in self.methods:
            if self.obj.__class__.__name__ == 'Email':  # email does not have total_duration so, excluded
                (getattr(self.obj, method)())
            elif method not in self.repeatable_methods and self.obj.__class__.__name__ != 'Email':
                (getattr(self.obj, method)())
            elif method in self.repeatable_methods:  # scheduling methods itself (not process)
                start_time = time.time()
                job_id = schedule.every(1).second.do((getattr(self.obj, method)))
                while time.time() - start_time < int(self.obj.total_duration)/n_repeatable_methods:
                    # predefine duration/number of repeatable methods
                    schedule.run_pending()
                    time.sleep(self.obj.iat)
                schedule.cancel_job(job_id)  # remove the job from schedule list


# ---browsing class
class Browsing:
    def __init__(self, name: str, url: str, delay_to_run_next_process, total_duration: int, bot_name,
                 required_login: bool = False, iat: int = 30,
                 driver_name: str = 'chromedriver'):
        self.name = name
        self.url = url
        self.delay_to_run_next_process = delay_to_run_next_process
        self.total_duration = total_duration
        self.required_login = required_login
        self.driver_name = driver_name
        self.iat = iat  # delay between execution of repeatable methods
        # we do not want to initialize the driver when the obj is created so we don't use self.__driverInit__() in the object instantiation method
        # We rather add this method forcefully at the beginning of actionList
        # self.__driverInit__() # this is an special and compulsary method that should be executed before any other method first in browsing. So, I put it here in init
        self.bot_name = bot_name

    def __driverInit__(self):  # I name it starting with "__ " to be not selected as method to object lists
        # initiate the driver. n.b.: for windows machines not no execution path is required
        options = webdriver.ChromeOptions()
        # options.add_argument("start-maximized")
        options.add_argument("--disable-notifications")
        options.add_argument("disable-infobars")
        options.add_argument("--disable-extensions")
        # check for OS name: for linux, we search for the driver within the machine, having the exact name such as 'chromedriver'
        if platform.system() == "Linux":
            for root, dirs, files in os.walk('/home/'):
                if self.driver_name in files:
                    driver_path = os.path.join(root, self.driver_name)
                    self.driver = webdriver.Chrome(chrome_options=options, executable_path=driver_path)
        elif platform.system() == "Windows":
            self.driver = webdriver.Chrome(chrome_options=options)
        print(f'{dt.now()} Driver Initialized for {self.name} --------------Opening link{self.url}.........', file=open(log_txt_file_path, 'a'))
        save_logs(self.bot_name, f'Driver Initialized for {self.name} --------------Opening link{self.url}.........')
        self.driver.get(self.url)

    def __acceptCookiesConsent__(self, xpath: str = None):
        print(f'{dt.now()} Accept/reject cookies or consents if necessary....................', file=open(log_txt_file_path, 'a'))
        save_logs(self.bot_name, f'Accept/reject cookies or consents if necessary')
        try:
            time.sleep(5)
            accept_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
            accept_button.click()
            # self.driver.find_element(By.XPATH, xpath).click()
            # sleep 5s since YouTube takes time to reload after giving the consent
            time.sleep(5)
        except Exception as e:
            print(f'{dt.now()} Exception {e} for {self.name}', file=open(log_txt_file_path, 'a'))



    def scrolDown(self):
        print(f'{dt.now()} {self.name}: scroll down', file=open(log_txt_file_path, 'a'))
        save_logs(self.bot_name, f'{self.name}: scroll down')
        # Get scroll height
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        # scroll the page 5 time
        for i in range(random.randint(2, 4)):
            # Scroll down to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Wait to load page
            time.sleep(random.randint(10, 30))
            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def __closing__(self):
        # Named with __ to be considered as special method. This method should not be selected in the list. Imagine this method selected as the first method!!! In Python, double underscore (also known as "dunder")
        print(f'{dt.now()} {self.name}: closing page {self.url}', file=open(log_txt_file_path, 'a'))
        save_logs(self.bot_name, f'{self.name}: closing page {self.url}')
        self.driver.close()  # only closes the corresponding window


# google, ddgo, booking.com, amazon can be directly created from this class
class BrowseNSearch(Browsing):
    def __init__(self, name: str, url: str, delay_to_run_next_process, total_duration: int, bot_name,
                 required_login: bool = False, iat: int = 30, search_keyword: str = 'places'):
        super().__init__(name, url, delay_to_run_next_process, total_duration, bot_name, required_login, iat)
        self.search_keyword = search_keyword
        self.consent_xpath = ''
        self.bot_name = bot_name
    def doSearch(self):
        print(f'{dt.now()} {self.name} : The search results for: {self.search_keyword}', file=open(log_txt_file_path, 'a'))
        save_logs(self.bot_name, f'{self.name} : The search results for: {self.search_keyword}')
        # find the search-box
        time.sleep(5)
        try:
            if self.url.find('amazon') != -1:
                search_box = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'twotabsearchtextbox')))
            elif self.url.find('booking') != -1:
                search_box = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.NAME, 'ss')))
                # search_box = self.driver.find_element(By.NAME, 'ss')
            else:
                if self.url.find('google') != -1:
                    self.__acceptCookiesConsent__(xpath=self.consent_xpath)
                search_box = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.NAME, 'q')))
                # search_box = self.driver.find_element(By.NAME, "q")
            search_box.send_keys(self.search_keyword)
            search_box.submit()
        except Exception as e:
            print(f'{dt.now()} Exception {e} for {self.name}: check the Name/xpath of the search box', file=open(log_txt_file_path, 'a'))

    def __collectLinks__(self):
        print(f'{dt.now()} {self.name} : Collecting links: {self.search_keyword}', file=open(log_txt_file_path, 'a'))
        save_logs(self.bot_name, f'{self.name} : Collecting links: {self.search_keyword}')
        # Wait for the search result to load
        time.sleep(5)
        # self.driver.implicitly_wait(10)
        # Get the HTML content of the search result page
        html = self.driver.page_source
        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        # Collect all the links from the search result
        links = []
        for link in soup.find_all("a"):
            href = link.get("href")
            if href and href.lower().startswith('https://'):
                links.append(href)
        links = list(set(links))  # remove the duplicates
        return links[5:]

    def clickPlayLink(self, n_rand_links=5):
        self.doSearch()
        print(f'{dt.now()} {self.name} : Clicking links: {self.search_keyword}', file=open(log_txt_file_path, 'a'))
        save_logs(self.bot_name, f'{self.name} : Clicking links: {self.search_keyword}')
        links = self.__collectLinks__()
        # visit several links randomly
        for i in range(n_rand_links):
            print(f'{dt.now()} {self.name} : Clicking link {i}', file=open(log_txt_file_path, 'a'))
            save_logs(self.bot_name, f'{self.name} : Clicking link {i}')
            ridx = random.randint(0, len(links) - 1)
            try:
                self.driver.get(links[ridx])
            except:
                print(f'{dt.now()} site not reachable', file=open(log_txt_file_path, 'a'))
                save_logs(self.bot_name, f'site not reachable')
            time.sleep(random.randint(10, 30))



class BrowseGoogle(BrowseNSearch):
    def __init__(self, name: str, url: str, delay_to_run_next_process, total_duration: int, bot_name,
                 required_login: bool = False, iat: int = 30, search_keyword: str = 'hacking'):
        super().__init__(name, url, delay_to_run_next_process, total_duration, bot_name, required_login, iat)
        self.search_keyword = search_keyword
        self.consent_xpath = '//*[@id="L2AGLb"]/div'
        self.bot_name = bot_name

    def clickPlayLink(self, n_rand_links=5):
        self.doSearch()
        print(f'{dt.now()} {self.name} : Clicking links: {self.search_keyword}', file=open(log_txt_file_path, 'a'))
        save_logs(self.bot_name, f'{self.name} : Clicking links: {self.search_keyword}')
        links = self.__collectLinks__()
        # visit several links randomly
        for i in range(n_rand_links):
            print(f'{dt.now()} {self.name} : Clicking link {i}', file=open(log_txt_file_path, 'a'))
            save_logs(self.bot_name, f'{self.name} : Clicking link {i}')
            ridx = random.randint(0, len(links) - 1)
            self.driver.get(links[ridx])
            time.sleep(random.randint(10, 30))



class BrowseYoutube(BrowseNSearch):
    def __init__(self, name: str, url: str, delay_to_run_next_process, total_duration: int, bot_name,
                 required_login: bool = False, iat: int = 30, search_keyword: str = 'hacking'):
        super().__init__(name, url, delay_to_run_next_process, total_duration, bot_name, required_login, iat)
        self.search_keyword = search_keyword
        self.consent_xpath = '/html/body/ytd-app/ytd-consent-bump-v2-lightbox/tp-yt-paper-dialog/div[4]/div[2]/div[6]/div[1]/ytd-button-renderer[2]/yt-button-shape/button/yt-touch-feedback-shape/div/div[2]'
        self.yt_vdo_xpath = '//*[@id="video-title"]/yt-formatted-string'
        self.yt_ad_button = '/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[1]/div[2]/div/div/ytd-player/div/div/div[17]/div/div[3]/div/div[2]/span/button'
        self.bot_name = bot_name
    # youtubes search result page is dynamic, which means that the search results are loaded dynamically using JavaScript
    # This can make it more difficult to scrape the page using traditional web scraping tools like BeautifulSoup.
    # Thus, we will modify it to limited feature like search and click only first link

    def doSearch(self):
        self.__acceptCookiesConsent__(self.consent_xpath)
        print(f'{dt.now()} {self.name} : The search results for: {self.search_keyword}', file=open(log_txt_file_path, 'a'))
        save_logs(self.bot_name, f'{self.name} : The search results for: {self.search_keyword}')
        # find the search-box
        time.sleep(5)
        try:
            search_box = self.driver.find_element(By.NAME, "search_query")
            search_box.send_keys(self.search_keyword)
            search_box.submit()
        except Exception as e:
            print(f'{dt.now()} Exception {e} for {self.name}: check the Name/xpath of the search box', file=open(log_txt_file_path, 'a'))


    def clickPlayLink(self, keyword: str = None, n_rand_links=5):
        self.doSearch()
        try:
            # find element with explicit wait
            time.sleep(5)
            print(f'{dt.now()} {self.name} : Playing video on YouTube for: {self.search_keyword}', file=open(log_txt_file_path, 'a'))
            save_logs(self.bot_name, f'{self.name} : Playing video on YouTube for: {self.search_keyword}')
            play = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, self.yt_vdo_xpath)))
            play.click()
            time.sleep(5)
            self.driver.find_element(By.XPATH, self.yt_ad_button).click()
        except Exception as e:
            print(f'{dt.now()} Exception {e} for {self.name}: check the xpath of video or ad button', file=open(log_txt_file_path, 'a'))


class BrowseFacebook(BrowseNSearch):
    def __init__(self, name: str, url: str, delay_to_run_next_process, total_duration: int, bot_name,
                 required_login: bool = True, iat: int = 30, search_keyword: str = 'science'):
        super().__init__(name, url, delay_to_run_next_process, total_duration, bot_name, required_login, iat)
        self.fb_consent_xpath = '/html/body/div[3]/div[2]/div/div/div/div/div[4]/button[2]'
        self.fb_user = 'tnikola230@gmail.com'
        self.fb_pass = 'tucKN2022'
        self.fb_loginButton_xpath = '/html/body/div[1]/div[1]/div[1]/div/div/div/div[2]/div/div[1]/form/div[2]/button'
        self.search_keyword = search_keyword
        self.bot_name = bot_name

    def __login__(self):
        self.__acceptCookiesConsent__(xpath=self.fb_consent_xpath)
        time.sleep(5)
        self.driver.find_element(By.XPATH, '//*[@id="email"]').send_keys(self.fb_user)
        self.driver.find_element(By.XPATH, '//*[@id="pass"]').send_keys(self.fb_pass)
        self.driver.find_element(By.XPATH, self.fb_loginButton_xpath).click()  # click login button
        time.sleep(5)  # provide sufficient time to load the page
        print(f'{dt.now()} login successful to facebook', file=open(log_txt_file_path, 'a'))

    def doSearch(self):
        print(f'{dt.now()} {self.name} : The search results for: {self.search_keyword}', file=open(log_txt_file_path, 'a'))
        save_logs(self.bot_name, f'{self.name} : The search results for: {self.search_keyword}')
        # find the search-box
        try:
            time.sleep(5)
            search_box = self.driver.find_element(By.XPATH, "//input[@type='search']")
            # search_box = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@type='search']")))
            search_box.send_keys(self.search_keyword)
            search_box.send_keys(Keys.ENTER)
        except Exception as e:
            print(f'{dt.now()} Exception {e} for {self.name}: check the Name/xpath of the search box', file=open(log_txt_file_path, 'a'))

    def clickPlayLink(self, n_rand_links=2):
        self.doSearch()
        print(f'{dt.now()} {self.name} : Clicking links: {self.search_keyword}', file=open(log_txt_file_path, 'a'))
        save_logs(self.bot_name, f'{self.name} : Clicking links: {self.search_keyword}')
        links = self.__collectLinks__()
        for i in range(n_rand_links):
            print(f'{dt.now()} {self.name} : Clicking link {i}', file=open(log_txt_file_path, 'a'))
            save_logs(self.bot_name, f'{self.name} : Clicking link {i}')
            ridx = random.randint(0, len(links) - 1)
            self.driver.get(links[ridx])
            self.scrolDown()

class BrowseLinkedin(BrowseNSearch):
    def __init__(self, name: str, url: str, delay_to_run_next_process, total_duration: int, bot_name,
                 required_login: bool = True, iat: int = 30, search_keyword: str = 'cybersecurity'):
        super().__init__(name, url, delay_to_run_next_process, total_duration, bot_name, required_login, iat)
        self.l_user = 'tnikola230@gmail.com'
        self.l_pass = 'tucKN2022'
        self.search_keyword = search_keyword

    def __login__(self):
        self.driver.find_element(By.XPATH, '/html/body/nav/div/a[2]').click()  # click on the sign in button
        time.sleep(5)
        login = self.driver.find_element(By.XPATH, '//*[@id="username"]')
        login.send_keys(self.l_user)
        login = self.driver.find_element(By.XPATH, '//*[@id="password"]')
        login.send_keys(self.l_pass)
        login.send_keys(Keys.ENTER)
        try:
            self.driver.find_element(By.XPATH, '//*[@id="ember455"]/button').click()
        except:
            print(f'{dt.now()} Scip verification was not required:', file=open(log_txt_file_path, 'a'))
        time.sleep(5)
        print(f'{dt.now()} login successfully to Linkedin', file=open(log_txt_file_path, 'a'))

    def doSearch(self):
        print(f'{dt.now()} {self.name} : The search results for: {self.search_keyword}',
              file=open(log_txt_file_path, 'a'))
        save_logs(self.bot_name, f'{self.name} : The search results for: {self.search_keyword}')
        # find the search-box
        try:
            # Jobs page
            self.driver.get('https://www.linkedin.com/jobs/')
            time.sleep(5)
            # go to search page directly
            self.driver.get(
                f'https://www.linkedin.com/jobs/search/?currentJobId=3364206951&geoId=101282230&keywords={self.search_keyword}&location=Germany&refresh=true')
            time.sleep(5)
        except Exception as e:
            print(f'{dt.now()} Exception {e} for {self.name}: check the Name/xpath of the search box',
                  file=open(log_txt_file_path, 'a'))

    def __collectLinks__(self):
        # Get all links for these offers
        links = []
        # Navigate 3 pages
        print(f'{dt.now()} {self.name} : Collecting links: {self.search_keyword}', file=open(log_txt_file_path, 'a'))
        save_logs(self.bot_name, f'{self.name} : Collecting links: {self.search_keyword}')
        try:
            for page in range(2, 5):
                time.sleep(5)
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

                print(f'{dt.now()} {self.name} : Collecting the links in the page: {page - 1}', file=open(log_txt_file_path, 'a'))
                save_logs(self.bot_name, f'{self.name} : Collecting the links in the page: {page - 1}')
                # go to next page:
                self.driver.find_element(By.XPATH, f"//button[@aria-label='Page {page}']").click()
                time.sleep(5)
        except Exception as e:
            print(f'{dt.now()} {e}', file=open(log_txt_file_path, 'a'))
        return links


class Chatting:
    # U may use this library Skype4Py: check example on gpt3
    def __init__(self, name, total_duration, sender_email, sender_password, sender_username, receiver_username, bot_name,
                 receiver_skypename, text_list, delay_to_run_next_process, required_login: bool = True, iat: int = 30):
        self.required_login = required_login
        self.name = name
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.sender_username = sender_username
        self.receiver_username = receiver_username
        self.receiver_skypename = receiver_skypename
        self.texts = text_list
        self.iat = iat
        self.delay_to_run_next_process = delay_to_run_next_process
        self.total_duration = total_duration
        # it is good idea put login in the init see ftp example
        self.bot_name = bot_name

    def __login__(self):
        # Create a Skype object and log in
        self.skype = Skype(self.sender_email, self.sender_password)
        print(f'{dt.now()} logged in as: {self.sender_username}', file=open(log_txt_file_path, 'a'))
        save_logs(self.bot_name, f'{self.name} : logged in as: {self.sender_username}')

    def chat_with(self):
        # time.sleep(10)
        print(f'{dt.now()} {self.sender_username} is Chatting with {self.receiver_username}',
              file=open(log_txt_file_path, 'a'))
        save_logs(self.bot_name, f'{self.name} : {self.sender_username} is Chatting with {self.receiver_username}')
        # Find the contact to send the message to
        contact = self.skype.contacts[self.receiver_skypename]
        # Send a message to the contact
        contact.chat.sendMsg(random.choice(self.texts))


class Email:
    def __init__(self, name, delay_to_run_next_process, subject, mailbody, sender_email, receiver_email, bot_name,
                 cc_email, bcc_email, mail_server, attach_addr: str = '', required_login: bool = True, iat: int = 30):
        self.required_login = required_login
        self.name = name
        self.delay_to_run_next_process = delay_to_run_next_process
        self.required_login = required_login
        self.attach_addr = attach_addr
        self.subject = subject
        self.mailbody = mailbody
        self.sender_email = sender_email
        self.receiver_email = receiver_email
        self.cc_email = cc_email
        self.bcc_email = bcc_email
        self.iat = iat
        self.bot_name = bot_name
        self.mail_server = mail_server

    def __login__(self):
        print(f'{dt.now()} Login into email', file=open(log_txt_file_path, 'a'))
        save_logs(self.bot_name, f'{self.name} : Login to email')

    def addAttachment(self):
        # Open PDF file in binary mode
        with open(self.attach_addr, "rb") as attachment:
            # Add file as application/octet-stream
            # Email client can usually download this automatically as attachment
            self.part = MIMEBase("application", "octet-stream")
            self.part.set_payload(attachment.read())
        # Encode file in ASCII characters to send by email
        encoders.encode_base64(self.part)
        # Add header as key/value pair to attachment part
        filename_filtered = re.split("([^\/]+$)", self.attach_addr)  # finters the filename from the path
        self.part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename_filtered[1]}",
        )
        # check if it is not bigger than X size: X is max value size in EmailCow
        print(f'{dt.now()} attach file in {filename_filtered} is loaded ', file=open(log_txt_file_path, 'a'))
        save_logs(self.bot_name, f'{self.name} : attach file in {filename_filtered} is loaded ')

    def __send_email__(self):
        # Create a multipart message and set headers
        message = MIMEMultipart()
        message["From"] = self.sender_email
        message["To"] = self.receiver_email
        message["Subject"] = self.subject
        message["cc"] = self.cc_email
        message["Bcc"] = self.bcc_email
        # Add body to email
        message.attach(MIMEText(self.mailbody, "plain"))
        # Add attachment to message and convert message to string
        self.addAttachment()
        try:
            message.attach(self.part)
        except:
            print(f'{dt.now()} Sending email without attachment', file=open(log_txt_file_path, 'a'))
            save_logs(self.bot_name, f'{self.name} : Sending email without attachment')
        text = message.as_string()
        with smtplib.SMTP(self.mail_server) as server:
            server.sendmail(self.sender_email, self.receiver_email, text)
            print(f'{dt.now()} Successfully sent email', file=open(log_txt_file_path, 'a'))
            save_logs(self.bot_name, f'{self.name} : Successfully sent email')
        # when Email obj is created, it means we should send email. So, we need default values to send email even if we did run methos like email_body or email_attach
        # so we should declare compulsary args in init
        print(f'{dt.now()} Sending email to {self.receiver_email}', file=open(log_txt_file_path, 'a'))
        save_logs(self.bot_name, f'{self.name} : Sending email to {self.receiver_email}')


class FTPClient:  # for ftp client u can use ftplib, see example in chatgpt3
    def __init__(self, name, delay_to_run_next_process, user, password, ip, bot_name, ftp_filename: str = '',
                 required_login: bool = True, iat: int = 30):
        self.name = name  # object name like ftp_1
        self.delay_to_run_next_process = delay_to_run_next_process
        self.user = user
        self.password = password
        self.ip = ip
        self.ftp_filename = ftp_filename
        self.required_login = required_login
        self.iat = iat
        self.bot_name = bot_name

    def __login__(self):
        try:
            self.ftp = ftplib.FTP(self.ip)
            self.ftp.login(user=self.user, passwd=self.password)
            print(f'{dt.now()} Login to FTP with IP: {self.ip} user:{self.user} and password: {self.password}',
                  file=open(log_txt_file_path, 'a'))
            save_logs(self.bot_name, f'Login to FTP with IP: {self.ip} user:{self.user} and password: {self.password}')
        except:
            print(f'{dt.now()} FTP server not reachable')
            save_logs(self.bot_name, f'{self.name} : FTP server not reachable')

    def download(self):
        self.ftp.cwd("/downloadable_files/")
        # print(self.ftp.pwd())
        # print(ftplib.FTP.dir(self.ftp))
        with open(self.ftp_filename, 'wb') as file:
            self.ftp.retrbinary(f"RETR {self.ftp_filename}", file.write)
            print(f'{dt.now()} downloading {self.ftp_filename} to ftp......... ', file=open(log_txt_file_path, 'a'))
            save_logs(self.bot_name, f'downloading {self.ftp_filename} to ftp server')
        self.ftp.quit()


class BotGenerator:
    def __init__(self, total_bot_duration: int, n_normal_bots: int, n_cd_bots: int, warmup_period: int):
        self.total_bot_duration = total_bot_duration * 60  # the total duration is provided in minutes. So we convert it to seconds
        self.n_normal_bots = n_normal_bots
        self.n_cd_bots = n_cd_bots
        self.warmup_period = warmup_period
        self.normalbotList = []
        self.cdBotList = []
        
        # bot objects are generated at the object instantiation. Other features are added subsequently
        self.spawn_bots()

    def spawn_bots(self):
        # generate the regular bots
        for i in range(self.n_normal_bots):
            bot = NormalBot(f'normal_bot_{i}')
            self.normalbotList.append(bot)
        # generate the CD bots
        if self.n_cd_bots is not None or self.n_cd_bots != 0:
            for i in range(self.n_cd_bots):
                bot = NormalBot(f'cd_bot_{i}')
                self.cdBotList.append(bot)

    def get_file_path(self, relative_path):
        # a helper function to convert all the file paths from relative path to absolute path
        # we consider the 'oop' dir to be the root directory of the project
        # that means all files should be stored inside 'oop' or a subdirectory of it
        current_file_path = os.path.abspath(__file__)
        current_dir = os.path.dirname(current_file_path) or '.'
        if platform.system() == "Windows":
            return os.path.join(current_dir, relative_path).replace('\\', '/')
        else:
            return os.path.join(current_dir, relative_path)

    def get_config_params(self):
        with open(self.get_file_path('bot_config_parameters.yml')) as f:
            self.data = yaml.safe_load(f)
        self.browsing_params = self.data['browsing']
        self.weblinks = self.data['browsing']['websites']
        self.chatting_params = self.data['chatting']
        self.emailing_params = self.data['emailing']
        self.ftp_params = self.data['ftp']
        self.bot_specs = self.data['bot_specs']

    def get_bot_specs(self):
        # **********customizable variables************ #
        # Since we want to have the randomized but limited number of browsing/chatting/emailing object, we predefine the
        # range of values here to make the access easier for the user. Later we choose any value from these ranges randomly
        self.range_browsers_normal = self.bot_specs['range_browsers_normal']
        self.range_browsers_cd = self.bot_specs['range_browsers_cd']
        self.range_chats_normal = self.bot_specs['range_chats_normal']
        self.range_chats_cd = self.bot_specs['range_chats_cd']
        self.range_emails_normal = range(self.bot_specs['range_emails_normal']['lower'], self.bot_specs['range_emails_normal']['upper'])
        self.range_emails_cd = range(self.bot_specs['range_emails_cd']['lower'], self.bot_specs['range_emails_cd']['upper'])
        self.range_ftp_normal = range(self.bot_specs['range_ftp_normal']['lower'], self.bot_specs['range_ftp_normal']['upper'])
        self.range_ftp_cd = range(self.bot_specs['range_ftp_cd']['lower'], self.bot_specs['range_ftp_cd']['upper'])
        # We consider the time between execution of repeatable methods as IAT: Inter-arrival time
        self.lower_bound_iat = self.bot_specs['lower_bound_iat']
        self.higher_bound_iat = self.bot_specs['higher_bound_iat']
        self.lower_bound_iat_cd = self.bot_specs['lower_bound_iat']
        self.higher_bound_iat_cd = self.bot_specs['lower_bound_iat']

    def generate_browsing_objs(self, count, bot_list, execution_duration, drift=False):
        # here the count_range is the number of brwosing object to be created
        for bot in bot_list:
            # loop over number of browsers and create random objects
            for i in range(count):
                # choose iat randomly from range
                if drift:
                    iat = random.randint(self.lower_bound_iat_cd, self.higher_bound_iat_cd)
                else:
                    iat = random.randint(self.lower_bound_iat, self.higher_bound_iat)
                # choose a link randomly
                link = random.choice(self.weblinks)
                if isinstance(link, dict):
                    link = random.choice(link['browse_search'])
                    # to get the doamin name from the link, we do a regex filtering
                    # 1-optional match "http://" or "https://" >> 2-optional match @ >> 3-optional match "www."
                    # finally match the domain except colons. Then we split into list and take the 2nd value(the name)
                    # domain = re.split('^(?:https?:\/\/)?(?:[^@\n]+@)?(?:www\.)?([^:\/\n]+)', link)
                    if 'amazon' in link:
                        search_keyword = random.choice(self.browsing_params['amazon_search_keywords'])
                    elif 'booking' in link:
                        search_keyword = random.choice(self.browsing_params['hotel_search_keywords'])
                    else:
                        search_keyword = random.choice(self.browsing_params['general_search_keywords'])
                    browser = BrowseNSearch(name=f'browse_search{i}', url=link,
                                             delay_to_run_next_process=random.randint(10, 60), iat=iat,
                                             total_duration=execution_duration, search_keyword=search_keyword, bot_name=bot.name)
                else:
                    if 'linkedin' in link.lower():
                        browser = BrowseLinkedin(name=f'linkedin{i}', url=link, delay_to_run_next_process=random.randint(10, 60),
                                                 total_duration=execution_duration, iat=iat,
                                                 search_keyword=random.choice(self.browsing_params['job_search_keywords']),
                                                 bot_name=bot.name)
                    elif 'facebook' in link.lower():
                        browser = BrowseFacebook(name=f'facebook{i}', url=link,
                                                 delay_to_run_next_process=random.randint(10, 60),
                                                 total_duration=execution_duration, iat=iat,
                                                 search_keyword=random.choice(self.browsing_params['general_search_keywords']),
                                                 bot_name=bot.name)
                    elif 'google' in link.lower():
                        browser = BrowseGoogle(name=f'google{i}', url=link,
                                                 delay_to_run_next_process=random.randint(10, 60),
                                                 total_duration=execution_duration, iat=iat,
                                               search_keyword=random.choice(self.browsing_params['general_search_keywords']),
                                               bot_name=bot.name)
                    elif 'youtube' in link.lower():
                        if drift is True:
                            search_keyword = f"\"{random.choice(self.browsing_params['general_search_keywords'])}\" \"quality:4k\""
                        else:
                            search_keyword = random.choice(self.browsing_params['general_search_keywords'])
                        browser = BrowseYoutube(name=f'youtube{i}', url=link,
                                                 delay_to_run_next_process=random.randint(10, 60), iat=iat,
                                                 total_duration=execution_duration, search_keyword=search_keyword,
                                                bot_name=bot.name)
                    else:
                        # get the domain name
                        # domain = re.split('^(?:https?:\/\/)?(?:[^@\n]+@)?(?:www\.)?([^:\/\n]+)', link)
                        browser = Browsing(name=f'browser{i}', url=link, delay_to_run_next_process=random.randint(10, 60),
                                           iat=iat, total_duration=execution_duration, bot_name=bot.name)
                bot.addBrowse(browser)

    def generate_chatting_objs(self, count, bot_list, execution_duration, drift=False):
        # here the count_range is the number of brwosing object to be created
        for bot in bot_list:
            # loop over number of chatting and create random objects
            for i in range(count):
                # choose iat randomly from range
                if drift:
                    iat = random.randint(self.lower_bound_iat_cd, self.higher_bound_iat_cd)
                else:
                    iat = random.randint(self.lower_bound_iat, self.higher_bound_iat)
                # Pick a random sender from the config file
                sender = random.choice(self.chatting_params['skype'])
                # Choose a receiver randomly
                receiver = random.choice(self.chatting_params['skype'])
                while sender == receiver:
                    receiver = random.choice(self.chatting_params['skype'])
                chat_obj = Chatting(name=f'chat{i}', total_duration=execution_duration, sender_email=sender['email'],
                                    sender_password=sender['password'], sender_username=sender['username'],
                                    receiver_username=receiver['username'], receiver_skypename=receiver['skypename'],
                                    text_list=self.chatting_params['texts'], delay_to_run_next_process=random.randint(10, 60),
                                    iat=iat, bot_name=bot.name)
                bot.addChat(chat_obj)

    def generate_mailinging_objs(self, count_range, bot_list):
        # here the count_range is the number of brwosing object to be created
        for bot in bot_list:
            # loop over number of emailing and create random objects
            for i in range(random.randint(count_range.start, count_range.stop)):
                # pick a random sender
                sender_email = random.choice(self.emailing_params['mailcow'])['email']
                # pick random receivers
                receiver_email = random.choice(self.emailing_params['mailcow'])['email']
                cc_email = random.choice(self.emailing_params['mailcow'])['email']
                bcc_email = random.choice(self.emailing_params['mailcow'])['email']
                # pick random subjects
                subject = random.choice(self.emailing_params['subject'])
                # pick random mail bodies
                mailbody = random.choice(self.emailing_params['mailbody'])
                attach_addr = self.get_file_path(random.choice(self.emailing_params['attachments']))
                mail_obj = Email(name=f'email{i}', delay_to_run_next_process=random.randint(10, 30), subject=subject,
                                 mailbody=mailbody, sender_email=sender_email, receiver_email=receiver_email,
                                 cc_email=cc_email, bcc_email=bcc_email, mail_server=self.emailing_params['mail_server'],
                                 attach_addr=attach_addr, bot_name=bot.name)
                bot.addEmail(mail_obj)

    def generate_ftp_objs(self, count_range, bot_list, drift=False):
        # here the count_range is the number of brwosing object to be created
        for bot in bot_list:
            # loop over number of chatting and create random objects
            for i in range(random.randint(count_range.start, count_range.stop)):
                # pick a random sender
                user = random.choice(self.ftp_params['users'])
                # pick random file
                if drift is True:
                    ftp_filename = random.choice(self.ftp_params['file_dir']['cd_files'])
                else:
                    ftp_filename = random.choice(self.ftp_params['file_dir']['normal_files'])
                ftp_obj = FTPClient(name=f'FTP{i}', delay_to_run_next_process=random.randint(10, 30),
                                    user=user['username'], password=user['pass'], ip=user['ip'],
                                    ftp_filename= ftp_filename, bot_name=bot.name)
                bot.addFTP(ftp_obj)

    def build_bots(self):
        # get the config parameters
        self.get_config_params()
        # get the specifications of bot abilities and from config file
        self.get_bot_specs()
        if self.n_normal_bots != 0:
            # ----------------generate normal bots
            # at first we collect the number of browsing objects and chatting objects
            browser_count = random.randint(self.range_browsers_normal['lower'], self.range_browsers_normal['upper'])
            chatting_count = random.randint(self.range_chats_normal['lower'], self.range_chats_normal['upper'])
            # only browser and chatting has repeatable methods. so it is required to define the total execution time for
            # these 2 object builders. So that for sequential execution, each object has enough time to execute all the methods 
            # within the total bot execution time duration
            execution_duration = self.total_bot_duration/(browser_count + chatting_count)
            self.generate_browsing_objs(browser_count, self.normalbotList, execution_duration)
            self.generate_chatting_objs(chatting_count, self.normalbotList, execution_duration)
            self.generate_mailinging_objs(self.range_emails_normal, self.normalbotList)
            self.generate_ftp_objs(self.range_ftp_normal, self.normalbotList)
            # --------------create random list of methods for each category
            for bot in self.normalbotList:
                print(f'{dt.now()} Getting action list for {bot.name}',file=open(log_txt_file_path, 'a'))
                save_logs(bot.name, f'Getting action list for {bot.name}')
                bot.get_action_list(bot.browseList, bot.chatList, bot.emailList, bot.FTPList)
                bot.create_combined_method_list(bot.chatList, bot.browseList, bot.emailList, bot.FTPList)

        if self.n_cd_bots != 0:
            # ---------------genrate bots for concept drift
            # at first we collect the number of browsing objects and chatting objects
            browser_count = random.randint(self.range_browsers_cd['lower'], self.range_browsers_cd['upper'])
            chatting_count = random.randint(self.range_chats_cd['lower'], self.range_chats_cd['upper'])
            # For CD the bots executing actions in parallel. So the total duration is the execution time
            self.generate_browsing_objs(browser_count, self.cdBotList, self.total_bot_duration, True)
            self.generate_chatting_objs(chatting_count, self.cdBotList, self.total_bot_duration, True)
            self.generate_mailinging_objs(self.range_emails_cd, self.cdBotList)
            self.generate_ftp_objs(self.range_ftp_cd, self.cdBotList, True)
            # --------------create random list of methods for each category
            for bot in self.cdBotList:
                print(f'{dt.now()} Getting action list for {bot.name}', file=open(log_txt_file_path, 'a'))
                save_logs(bot.name, f'Getting action list for {bot.name}')
                bot.get_action_list(bot.browseList, bot.chatList, bot.emailList, bot.FTPList)
                bot.create_combined_method_list(bot.chatList, bot.browseList, bot.emailList, bot.FTPList)

    def save_bots(self):
        for bot in self.normalbotList:
            with open(self.get_file_path(f'normal_bots/{bot.name}.pickle'), 'wb') as f:
                pickle.dump(bot, f)
        for bot in self.cdBotList:
            with open(self.get_file_path(f'cd_bots/{bot.name}.pickle'), 'wb') as f:
                pickle.dump(bot, f)


