# Save cardlists for each commander to pickle files.
# Adapted from https://github.com/AlteriusOmega/edhrec_json_to_txt
import argparse
import os
import pickle
import re
import requests
import signal
import sys
import time
from tqdm import tqdm
from unidecode import unidecode

DATA_PATH = os.path.abspath(os.path.join('..','data'))
CARDLISTS_PATH = os.path.join(DATA_PATH,'edhreclists.pkl')

def format_card_name(card_name:str):
    first_card = card_name.split("//")[0].strip() # If the card is a split card, only use the first card
    non_alphas_regex = "[^\w\s-]" # Remove everything that's not alphanumeric or space or hyphen
    formatted_name = unidecode(first_card) # remove diacritics
    formatted_name = re.sub(non_alphas_regex, "", formatted_name)
    formatted_name = formatted_name.lower() # Make lowercase
    formatted_name = formatted_name.replace(" ", "-")  # Replace spaces with hyphens
    formatted_name = re.sub(r"-+", "-", formatted_name) # do not have multiple hyphens
    # print(f"In format_commander_name and formatted name is {formatted_name}")
    return formatted_name

def request_json(name:str, is_commander, redirect=''):
    formatted_name = format_card_name(name)
    if redirect:
        print(f"Redirected to {redirect}")
        json_url = f"https://json.edhrec.com/pages{redirect}.json"
    else:
        json_url = f"https://json.edhrec.com/pages/{'commanders' if is_commander else 'cards'}/{formatted_name}.json"
    response = requests.get(json_url)
    if response.status_code == 200:
        json_data = response.json()
        if 'redirect' in json_data:
            return request_json(name, is_commander,redirect=json_data['redirect'])
        # print(f"JSON request successful!")
        return json_data
    else:
        print(f"JSON request for \"{name}\" ({formatted_name}) failed! Try different card name")

def main():
    lists = {}
    def cleanup (signum, frame):
        """
        Clean up and close results files - in case of process killed.
        """
        if signum:
            print(f'Process killed on {time.asctime(time.localtime())}, with signal number {signum}.')
        # save cards
        with open(CARDLISTS_PATH, 'wb') as f:
                pickle.dump(lists, f)
        sys.exit()
    signal.signal(signal.SIGTERM, cleanup)
    signal.signal(signal.SIGINT, cleanup)
    try:
        # read in commanders
        with open(CARDLISTS_PATH, 'rb') as f:
            commanders = pickle.load(f)

        # read in previously-queried cardlists
        if os.path.isfile(os.path.join(DATA_PATH,'edhreclists.pkl')):
            with open(os.path.join(DATA_PATH,'edhreclists.pkl'), 'rb') as f:
                lists = pickle.load(f)
        if 'non_commander' not in lists:
            lists['non_commander'] = {}

        # iterate through commanders, requesting cardlists
        for split in commanders:
            print(f"Processing commanders in {split} set.")
            if split not in lists:
                lists[split] = {}
            # unqueried = [name for name in commanders[split] if (name not in lists[split]) or (len(lists[split][name]) < 99)] # don't re-query commanders we already have.
            for commander_name in tqdm(commanders[split]):
                if commander_name not in lists[split]:
                    json_data = request_json(commander_name, True)
                    if json_data is None:
                        continue
                    cardlist = sorted(json_data['cardlist'], key=lambda card: card['num_decks'], reverse=True)
                    if len(cardlist) < 99:
                        continue
                    lists[split][commander_name] = {'cards':{card['name']:card['num_decks'] for card in cardlist},
                                                    'total':json_data['container']['json_dict']['card']['num_decks']}
                time.sleep(1) # wait a second - hopefully stops rate limit
                cardlist = lists[split][commander_name]['cards']
                for card in tqdm(cardlist): # add non_commander cards
                    if card['name'] not in lists['non_commander']:
                        lists['non_commander'][commander_name] = {}
                        card_json_data = request_json(card['sanitized'], False)
                        if card_json_data is None:
                            continue
                        card_cardlist = sorted(card_json_data['cardlist'], key=lambda card: card['num_decks'], reverse=True)
                        lists['non_commander'][card['name']] = {'cards':{card['name']:card['num_decks'] for card in card_cardlist},
                                                                'total':card_json_data['container']['json_dict']['card']['num_decks']}
    except Exception as e:
        print(e)
    finally:
        # save cardlists
        cleanup(None, None)

if __name__ == "__main__":
    main()
