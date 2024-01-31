# Save cardlists for each commander to pickle files.
# Adapted from https://github.com/AlteriusOmega/edhrec_json_to_txt
import argparse
import os
import pickle
import re
import requests
from tqdm import tqdm
from unidecode import unidecode

DATA_PATH = os.path.abspath(os.path.join('..','data'))

def format_commander_name(commander_name:str):
    non_alphas_regex = "[^\w\s-]" # Remove everything that's not alphanumeric or space or hyphen
    formatted_name = re.sub(non_alphas_regex, "", commander_name)
    formatted_name = formatted_name.lower() # Make lowercase
    formatted_name = formatted_name.replace(" ", "-")  # Replace spaces with hyphens
    formatted_name = unidecode(formatted_name)
    # print(f"In format_commander_name and formatted name is {formatted_name}")
    return formatted_name

def request_json(commander_name:str):
    formatted_name = format_commander_name(commander_name)
    json_url = f"https://json.edhrec.com/pages/commanders/{formatted_name}.json"
    response = requests.get(json_url)
    if response.status_code == 200:
        json_data = response.json()
        # print(f"JSON request successful!")
        return json_data
    else:
        print(f"JSON request for {commander_name} failed! Try different commander name")

def main():
    # read in commanders
    with open(os.path.join(DATA_PATH,'commanders.pkl'), 'rb') as f:
        commanders = pickle.load(f)

    # read in previously-queried cardlists
    lists = {}
    if os.path.isfile(os.path.join(DATA_PATH,'edhreclists.pkl')):
        with open(os.path.join(DATA_PATH,'edhreclists.pkl'), 'rb') as f:
            lists = pickle.load(f)

    # iterate through commanders, requesting cardlists
    for split in commanders:
        print(f"Processing commanders in {split} set.")
        if split not in lists:
            lists[split] = {}
        unqueried = [name for name in commanders[split] if name not in lists[split]] # don't re-query commanders we already have.
        for commander_name in tqdm(unqueried):
            json_data = request_json(commander_name)
            if json_data is None:
                continue
            cardlist = sorted(json_data['cardlist'], key=lambda card: card['num_decks'], reverse=True)
            lists[split][commander_name] = cardlist

    # save cardlists
    with open(os.path.join(DATA_PATH,'edhreclists.pkl'), 'wb') as f:
        pickle.dump(lists, f)

if __name__ == "__main__":
    main()
