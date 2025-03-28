import datetime
import time
import pandas as pd
from bs4 import BeautifulSoup
import warnings
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import json
import os

warnings.filterwarnings("ignore")


def driver_conn():
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--headless")      # Make the browser Headless. if you don't want to see the display on chrome just uncomment this
    chrome_options.add_argument("--log-level=3")    # Removes error/warning/info messages displayed on the console
    chrome_options.add_argument("--disable-infobars")  # Disable infobars ""Chrome is being controlled by automated test software"  Although is isn't supported by Chrome anymore
    chrome_options.add_argument("start-maximized")     # Make chrome window full screen
    chrome_options.add_argument('--disable-gpu')       # Disable gmaximizepu (not load pictures fully)
    # chrome_options.add_argument("--incognito")       # If you want to run browser as incognito mode then uncomment it
    chrome_options.add_argument("--disable-notifications")  # Disable notifications
    chrome_options.add_argument("--disable-extensions")     # Will disable developer mode extensions
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")    # retrieve_block
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])    # retrieve_block
    chrome_options.add_experimental_option('useAutomationExtension', False)    # retrieve_block
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36')    # retrieve_block
    chrome_options.add_argument('--accept=text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9')    # retrieve_block
    chrome_options.add_argument('--accept-encoding=gzip, deflate, br')    # retrieve_block
    chrome_options.add_argument('--accept-language=en-US,en;q=0.9')    # retrieve_block

    # chrome_options.add_argument('--blink-settings=imagesEnabled=false')
    # chrome_options.add_argument('--proxy-server=%s' % PROXY)
    # chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    # prefs = {"profile.managed_default_content_settings.images": 2}
    # chrome_options.add_experimental_option("prefs", prefs)   #we have disabled pictures (so no time is wasted in loading them)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=chrome_options)  # you don't have to download chromedriver it will be downloaded by itself and will be saved in cache
    return driver



# ================================================================================
#                         Selenium Driver get Links
# ================================================================================
def get_url():
    username_data = input("Input your username: ")
    password_data = input("Input your password: ")
    driver = driver_conn()
    print('==================== Getting url ====================')
    url = "https://login.thespeakerlab.com/internal_api/v2/search/community_members?page="
    driver.get("https://login.thespeakerlab.com/members")
    time.sleep(3)
    username = driver.find_element(By.ID, "user_email")
    password = driver.find_element(By.ID, "user_password")
    username.send_keys(str(username_data))
    time.sleep(1)
    password.send_keys(str(password_data))
    time.sleep(1)
    driver.find_element(By.NAME, "commit").click()
    WebDriverWait(driver, 30).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    time.sleep(4)
    page = 166
    while True:
        page += 1
        print(">>>>>>>>>>>>>>>>>>>>>> Page: " + str(page))
        driver.get(url + str(page) + "&sort=oldest&per_page=30&visible_in_member_directory=true&exclude_empty_name=true&exclude_empty_profiles=false")
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        d = json.loads(soup.text)
        lis = d['records']
        print("Listing here: ", len(lis))
        if len(lis) < 1:
            break
        for li in lis:
            link_id = ''
            location = ''
            bio = ''
            website = ''
            twitter = ''
            facebook = ''
            instagram = ''
            linkedin = ''
            try:
                bio = li['bio']
            except:
                pass
            try:
                link_id = "https://login.thespeakerlab.com/u/" + li['public_uid']
            except:
                pass
            try:
                location = li['profile_info']['location']
            except:
                pass
            try:
                website = li['profile_info']['website']
            except:
                pass
            try:
                twitter = li['profile_info']['twitter_url']
            except:
                pass
            try:
                facebook = li['profile_info']['facebook_url']
            except:
                pass
            try:
                linkedin = li['profile_info']['linkedin_url']
            except:
                pass
            try:
                instagram = li['profile_info']['instagram_url']
            except:
                pass
            data = {
                'links': link_id,
                'Bio': bio,
                'Location': location,
                'Website': website,
                'Twitter': twitter,
                'Facebook': facebook,
                'Linkedin': linkedin,
                'Instagram': instagram,
            }
            df = pd.DataFrame([data])
            df.to_csv('url.csv', mode='a', header=not os.path.exists('url.csv'), encoding='utf-8-sig', index=False)
    return driver

def get_data(driver):
    print('=================== Data Scraping ===================')
    df = pd.read_csv("url.csv")
    links = df['links'].values
    bios = df['Bio'].values
    locs = df['Location'].values
    webs = df['Website'].values
    twis = df['Twitter'].values
    febs = df['Facebook'].values
    lins = df['Linkedin'].values
    insts = df['Instagram'].values
    print('Total link: ' + str(len(links)))
    d = 0
    for i in range(0, len(links)):
        d += 1
        print('Getting Data: ' + str(d) + ' out of ' + str(len(links)))
        link = links[i]
        bio = bios[i]
        loc = locs[i]
        web = webs[i]
        twi = twis[i]
        feb = febs[i]
        lin = lins[i]
        inst = insts[i]

        driver.get(link)
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        name = ''
        mail = ''
        member_since = ''
        tags = ''
        try:
            name = soup.find('span', {'data-testid': 'member-name'}).text.replace('\n', '').strip()
        except:
            pass
        try:
            mail = soup.find('div', {'data-testid': 'profile-info-section'}).find('p').text.replace('\n', '').strip()
        except:
            pass
        try:
            member_since = soup.find('div', {'data-testid': 'profile-member-since'}).text.replace('\n', '').strip()
        except:
            pass
        try:
            des = soup.find('div', {'class': 'profile-drawer__about__tags'}).find_all('span', {'data-testid': 'member-tag-label'})
            tags = '\n'.join(d.get_text(separator=" ", strip=True) for d in des)
        except:
            pass
        data = {
            'Link': link,
            'Name': name,
            'Mail': mail,
            'Member Since': member_since,
            'Tags': tags,
            'Bio': bio,
            'Location': loc,
            'Website': web,
            'Twitter': twi,
            'Facebook': feb,
            'Linkedin': lin,
            'Instagram': inst,
        }
        df = pd.DataFrame([data])
        df.to_csv('Data.csv', mode='a', header=not os.path.exists('Data.csv'), encoding='utf-8-sig', index=False)
    driver.close()


if __name__ == '__main__':
    driver = get_url()
    get_data(driver)