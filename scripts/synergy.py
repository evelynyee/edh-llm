import argparse
import math
import os
import pickle
from scrape_cardlists import request_json, CARDLISTS_PATH
import signal
import sys
import time
from tqdm import tqdm
DECK_PATH = os.path.abspath(os.path.join('..', 'data','decks'))
BASIC_LANDS = ['Plains', 'Island', 'Swamp', 'Mountain', 'Forest', 'Wastes']

def synergy(a,b, lists, a_is_commander=False):
    """
    Calculate count-based synergy between two cards, according to EDHRec play data.
    If considering a commander, it should be the first card listed, and set a_is_commander to True.

    a: a card name
    b: a card name
    lists: a dictionary of cardlists, as returned by scrape_cardlists.py
    a_is_commander: a boolean indicating whether a is a commander card

    Return: a numerical score: log(ab_counts**2/(a_counts*b_counts))
    """
    # get a-card fequency
    a_set = False
    a_freq = 0
    a_cards = []
    if a_is_commander: # commander card
        for split in ['valid','test']:
            if a in lists[split]:
                a_freq = lists[split][a]['total']
                a_cards = lists[split][a]['cards']
                a_set = True
                break
    elif a in lists['non_commander']: # normal card we've already queried
        a_freq = lists['non_commander'][a]['total']
        a_cards = lists['non_commander'][a]['cards']
        a_set = True

    if not a_set: # need to query the API for a-card data
        a_data = None
        for _ in range(5):
            a_data = request_json(a,a_is_commander)
            if a_data is not None:
                break
        if a_data is None:
            raise ValueError('Failed to get data for card:',a)
        a_freq = a_data['container']['json_dict']['card']['num_decks']
        a_cards = {card['name']:card['num_decks'] for card in a_data['cardlist']}
        a_split = 'test' if a_is_commander else 'non_commander'
        lists[a_split][a] = {'cards':a_cards, 'total':a_freq} # save the data for later use
        print(f'Adding card to {a_split} list: {a}')

    # get a and b co-fequency
    if b in a_cards:
        ab_freq = a_cards[b]
    else: # cards don't co-occur. assume 1 co-occurrence for calculating logarithm
        ab_freq = 1

    # get b-card fequency
    b_set = False
    b_freq = 0
    if b in lists['non_commander']: # there can't be 2 commanders
        b_freq = lists['non_commander'][b]['total']
        b_set = True
    if not b_set: # need to query the API for a data
        b_data = None
        for _ in range(5):
            b_data = request_json(b,False)
            if b_data is not None:
                break
            print(repr(b))
        if b_data is None:
            raise ValueError('Failed to get data for card:',b)
        b_cards = {card['name']:card['num_decks'] for card in b_data['cardlist']}
        b_freq = b_data['container']['json_dict']['card']['num_decks']
        lists['non_commander'][b] = {'cards':b_cards, 'total':b_freq} # save the data for later use
        print(f'Adding card to non_commander list: {b}')

    ratio = ab_freq**2/(a_freq*b_freq) # squaring the numerator gives better spread
    return math.log(ratio), lists

def mean (l):
    return sum(l)/len(l)

def evaluate_deck(commander, deck, lists):
    commander_sim = []
    co_card_sim = []
    print(f'evaluating deck: {commander}')
    start = time.localtime()
    print(f'start time: {time.asctime(start)}')
    failed = set()
    for i in tqdm(range(len(deck))):
        card = deck[i]
        if card in failed:
            continue
        try:
            sim, lists = synergy(commander,card,lists, a_is_commander=True)
            commander_sim.append(sim)
            card_sim = []
            for j in range(len(deck)):
                b = deck[j]
                if i == j or b in failed: # ignore synergy with itself, ignore failed cards
                    continue
                try:
                    sim, lists = synergy(card, b, lists)
                    card_sim.append(sim)
                except ValueError as e: # b card not found
                    print(e)
                    failed.add(b)
                    continue
            co_card_sim.append(mean(card_sim))
        except ValueError as e:  # a card not found
            print(e)
            failed.add(a)
            continue
    end = time.localtime()
    print(f'end time: {time.asctime(end)}')
    print(f'time elapsed: {time.mktime(end) - time.mktime(start)} seconds')
    return mean(commander_sim), mean(co_card_sim), lists

# Set up command-line arguments parser
parser = argparse.ArgumentParser()

# Add arguments
parser.add_argument("--path", type=str, required=True,
                    help="directory that contains the text files of decklists to be evaluated.")
args = parser.parse_args()

# Load the previously-queried synergy data
lists = pickle.load(open(CARDLISTS_PATH, 'rb'))
deck_path = os.path.join(DECK_PATH, args.path) # path to the folder which has all of the decks of that type
print(deck_path)
synergy_path = os.path.join(deck_path, 'synergy.pkl')
syn_dict = {}
if os.path.isfile(synergy_path):
    with open(synergy_path, 'rb') as f:
        syn_dict = pickle.load(f)

# list of deck files
deckfiles = os.listdir(deck_path)
deckfiles = [f for f in deckfiles if f.endswith('.txt')]

def cleanup (signum, frame):
    """
    Clean up and save data before exiting.
    """
    if signum:
        print(f'Process killed on {time.asctime(time.localtime())}, with signal number {signum}.')
    print('Total decks evaluated:',len(syn_dict))
    pre_lists = pickle.load(open(CARDLISTS_PATH, 'rb'))
    if pre_lists != lists: # new cards were added, so save the updated lists
        print('Saving updated cardlists.')
        with open(CARDLISTS_PATH, 'wb') as f:
            pickle.dump(lists, f)
    if (not os.path.isfile(synergy_path)) or (pickle.load(open(synergy_path, 'rb'))!= syn_dict):
        print('Saving updated synergy scores.')
        with open(synergy_path, 'wb') as f:
            pickle.dump(syn_dict, f)
    sys.exit()
# perform cleanup if program is killed or interrupted
signal.signal(signal.SIGTERM, cleanup)
signal.signal(signal.SIGINT, cleanup)

for f in deckfiles:
    # read in deck from txt file
    deck = []
    with open(os.path.join(deck_path, f), 'r', encoding='utf-8') as file:
        deck = file.readlines()
    deck = [card.split(' ', 1)[1].strip() for card in deck
            if '{' not in card # ignore previous metrics
            and len(card.strip()) > 0 # ignore empty lines
            and card.split(' ', 1)[1].strip() not in BASIC_LANDS] # ignore basic lands
    if deck[0] in syn_dict: # already processed
        # print('Already processed:',syn_dict[deck[0]])
        continue
    else:
        print(f"Processing {deck_path} - {f}")
    print(deck)
    print(len(deck))

    # evaluate the deck
    mean_commander, mean_co_card, lists = evaluate_deck(deck[0], deck[1:], lists)
    record = {'commander_synergy':mean_commander, 'card_synergy':mean_co_card}
    syn_dict[deck[0]] = record
    print(record)
    print('Total decks evaluated:',len(syn_dict))

# save the updated synergy data
cleanup(False, None)
