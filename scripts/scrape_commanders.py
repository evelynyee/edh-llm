"""
Scrape commanders from EDHRec and perform validation-test split.
Save results to pickle file.
"""

import random
import requests
import json
import os
import pickle
from bs4 import BeautifulSoup

VALID = 100
TEST = 200

url = 'https://edhrec.com/commanders'
response = requests.get(url)
if response.status_code != 200:
    print("Failed to retrieve the webpage")
content = response.text
soup = BeautifulSoup(content, 'html.parser')

# select commander cardlist data
commanders = (json.loads(soup.select_one('#__NEXT_DATA__').get_text())
              ['props']['pageProps']['data']['cardlist'])

# get the unique commander  names
commander_names = set()
for card in commanders:
    commander_names.add(card['name'])
assert len(commander_names) > VALID+TEST # check that there are enough available commanders

# get random sample of commanders
commander_names = list(commander_names)
random.shuffle(commander_names)
test = commander_names[:TEST]
valid = commander_names[TEST:TEST+VALID]

# write commander names to pickle files
with open(os.path.abspath(os.path.join('..','data','commanders.pkl')), 'wb') as f:
    pickle.dump({'test':test,'valid':valid}, f)


