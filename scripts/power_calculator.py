
import time
import re
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


def calculate_power(filepath):
    # Path to your webdriver
    PATH = os.path.abspath("chromedriver.exe")


    # Initialize the WebDriver
    chrome_options = Options()
    chrome_options.add_argument("--headless") #Comment out this line to debug (will show browser)
    driver = webdriver.Chrome(options=chrome_options)

    # Open the website
    driver.get("https://edhpowercalculator.com/")

    try:
        # Wait for the decklist upload element to be available
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Do you have a decklist to upload?')]"))
        )
        button.click()

        file_input = driver.find_element(By.ID, 'list-upload')

        # Send the file path to the input element
        #file_input.send_keys('C:/Users/theod/edh-llm/data/test_deck.txt')
        file_input.send_keys(os.path.abspath("../data/test_deck.txt")) #TO BE REPLACED BY FILEPATH
        #print('sent file!')
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Import')]"))
        )
        button.click()

        # necessary to wait for site to generate power level, pending more intelligent fix (detecting js update on site)
        time.sleep(30)

        # Pull raw html and read strength tag
        html_source = driver.page_source
        pattern = r"<strong>(.*?)</strong>"

        # Overall power
        overall = re.findall(pattern, html_source, re.DOTALL)
        #print(overall[1])

        # CMC
        pattern = r"Average mana cost: (\d+)"
        cmc = re.search(pattern, html_source)
        #print(cmc[1])

        # Ramp Sources
        pattern = r"Amount of ramp: (\d+)"
        ramp = re.search(pattern, html_source)
        #print(ramp[1])

        # Card Advantage
        pattern = r"Amount of card advantage: (\d+)"
        card_adv = re.search(pattern, html_source)
        #print(card_adv[1])

        
        # Interaction
        pattern = r"Amount of interaction: (\d+)"
        interaction = re.search(pattern, html_source)
        #print(interaction[1])
    finally:
        # Close the browser after a delay or after certain actions
        driver.quit()
        return(overall[1],cmc[1], card_adv[1], interaction[1])



