
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


def calculate_power(filepath):
    """
    Reads deck text files and returns power level of deck

    Parameters:
        -filepath: path to deck file
    Returns:
        -dictionary with the following attributes:
            -overall: power score, refer to documentation for formula
            -cmc: average converted mana cost
            -ramp: amount of mana ramp cards
            -draw: amount of cards that draw more cards
            -interaction: amount of cards that remove/counter other cards
    """

    # Path to your webdriver
    PATH = os.path.abspath("chromedriver.exe")


    # Initialize the WebDriver
    chrome_options = Options()
    chrome_options.add_argument("--headless") #Comment out this line to debug (will show browser)
    chrome_options.add_argument('log-level=3')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')
    driver = webdriver.Chrome(options=chrome_options)

    # Open the website
    driver.get("https://mtg.cardsrealm.com/en-us/tools/commander-power-level-calculator")

    try:
        button = WebDriverWait(driver, 100).until(
            EC.element_to_be_clickable((By.ID, "tools_import"))
        )
        file_input = driver.find_element(By.ID, 'tools_import_input')

        # Send the file path to the input element
        #file_input.send_keys('C:/Users/theod/edh-llm/data/test_deck.txt')
        file_input.send_keys(os.path.abspath(filepath))
        #print('sent file!')

        # necessary to wait for site to generate power level, pending more intelligent fix (detecting js update on site)
        time.sleep(4)
        try:
            avg_cmc = int(driver.find_element(By.ID, "total_cmc").get_attribute("value")) / int(driver.find_element(By.ID, "total_counted").get_attribute("value"))
        except ZeroDivisionError:
            avg_cmc = 0
        #print(avg_cmc)

        # Overall power
        overall = driver.find_element(By.ID, 'power_level').text
        #print(overall)
        #Ramp
        ramp = int(driver.find_element(By.ID, "total_ramp").get_attribute("value"))

        
        draw = int(driver.find_element(By.ID, "total_draw").get_attribute("value"))

        tutor = int(driver.find_element(By.ID, "total_tutor").get_attribute("value"))

        interaction = int(driver.find_element(By.ID, "total_removal").get_attribute("value")) + int(driver.find_element(By.ID, "total_counterspell").get_attribute("value"))
        overall = 2 / avg_cmc + ( draw/2 + ramp/2) / 2 + interaction/20
    except Exception as e:
        # Close the browser after a delay or after certain actions
        print(e)
        driver.quit()
        time.sleep(600)
        calculate_power(filepath)
    finally:
        driver.quit()
        return({'overall':overall, 'cmc':avg_cmc, 'ramp':ramp, 'draw':draw, 'interaction':interaction})



