import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from google.oauth2.service_account import Credentials
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import gspread
import csv
import pandas as pd

chrome_options = Options()
prefs = {
    "profile.managed_default_content_settings.images": 2,  
    "profile.managed_default_content_settings.stylesheets": 2,  
    "profile.managed_default_content_settings.javascript": 2, 
    "profile.managed_default_content_settings.fonts": 2, 
    "profile.managed_default_content_settings.media": 2,  
    "profile.managed_default_content_settings.popups": 2,  
}
chrome_options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(options=chrome_options)
driver.get("https://www.chrono24.com/rolex/index.htm")

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

CREDENTIALS_FILE = 'auth.json'  
SHEET_NAME = 'watchesData' 

credentials = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
client = gspread.authorize(credentials)
sheet = client.open(SHEET_NAME).sheet1


links = []

def getLinks(link):

    driver.get(link)
    itemsArray = []

    items = driver.find_elements(By.CLASS_NAME, "js-article-item-container")
    for item in items:
        itemLink = item.find_element(By.CLASS_NAME, "block-item").get_attribute("href")
        itemsArray.append(itemLink)
        
    
    return itemsArray

def scrapeData(link):
    try:
        driver.get(link)

        try:
            title = driver.find_elements(By.CLASS_NAME, "m-y-0")[1].find_element(By.TAG_NAME, "span").text or ""
        except:
            title = ""

        try:
            price = driver.find_element(By.CLASS_NAME, "js-price-shipping-country").text or ""
            price = price.replace("$", "").strip()
        except:
            price = ""

        try:
            rating = driver.find_element(By.CLASS_NAME, "rating").text or ""
        except:
            rating = ""

        try:
            containerAll = driver.find_elements(By.TAG_NAME, "tbody") or ""
            container = containerAll[0]
        except:
            containerAll = ""
            container = None

        try:
            rows = container.find_elements(By.TAG_NAME, "tr")
        except:
            rows = []

        try:
            model = rows[3].find_elements(By.TAG_NAME, "td")[1].text or ""
            model = model.split("(")[0]
        except:
            model = ""

        try:
            caseMaterial = rows[6].find_elements(By.TAG_NAME, "td")[1].text or ""
        except:
            caseMaterial = ""

        try:
            braceletMaterial = rows[7].find_elements(By.TAG_NAME, "td")[1].text or ""
        except:
            braceletMaterial = ""

        try:
            yearOfProduction = rows[8].find_elements(By.TAG_NAME, "td")[1].text or ""
            yearOfProduction = yearOfProduction.split("(")[0].strip()
        except:
            yearOfProduction = ""

        try:
            conditionContainer = rows[9].find_elements(By.TAG_NAME, "td")[1] or ""
            condition = conditionContainer.find_element(By.TAG_NAME, "button").text or ""
        except:
            condition = ""

        try:
            gender = rows[11].find_elements(By.TAG_NAME, "td")[1].text or ""
        except:
            gender = ""

        try:
            secondContainer = containerAll[1]
            rows = secondContainer.find_elements(By.TAG_NAME, "tr")
        except:
            rows = []

        try:
            numberOfJewls = rows[5].find_elements(By.TAG_NAME, "td")[1].text or ""
        except:
            numberOfJewls = ""

        try:
            thirdContainer = containerAll[2]
            rows = thirdContainer.find_elements(By.TAG_NAME, "tr")
        except:
            rows = []

        try:
            diameter = rows[1].find_elements(By.TAG_NAME, "td")[1].text or ""
        except:
            diameter = ""

        try:
            waterResistance = rows[2].find_elements(By.TAG_NAME, "td")[1].text or ""
        except:
            waterResistance = ""

        try:
            fourthContainer = containerAll[2]
            rows = fourthContainer.find_elements(By.TAG_NAME, "tr")
        except:
            rows = []

        try:
            clasp = rows[3].find_elements(By.TAG_NAME, "td")[1].text or ""
        except:
            clasp = ""

        try:
            claspMaterial = rows[4].find_elements(By.TAG_NAME, "td")[1].text or ""
        except:
            claspMaterial = ""

        return [
            title, price, rating, model, caseMaterial, braceletMaterial,
            yearOfProduction, condition, gender, numberOfJewls, diameter,
            waterResistance, clasp, claspMaterial
        ]
    except Exception as e:
        print(f"Error while scraping data: {e}")
        return []



def getAllLinks():
    for i in range(402,500):
        print(f"current page {i}")
        linksList = getLinks(f"https://www.chrono24.com/rolex/index.htm?pageSize=120&showpage={i}")
        for link in linksList:
            
            watch = scrapeData(link)
            print(watch)
            sheet.append_row(watch)


    print(links)




getAllLinks()
 

