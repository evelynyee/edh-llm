import argparse
import math
import pickle
from scrape_cardlists import request_json, CARDLISTS_PATH

def synergy(a,b, lists, a_is_commander=False):
    """
    Calculate count-based synergy between two cards, according to EDHRec play data.
    If considering a commander, it should be the first card listed, and set a_is_commander to True.
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
        while a_data is None:
            a_data = request_json(a,a_is_commander)
        a_freq = a_data['container']['json_dict']['card']['num_decks']
        a_cards = {card['name']:card['num_decks'] for card in a_data['cardlist']}

    # get a and b co-fequency
    if b in a_cards:
        ab_freq = a_cards[b]
    else: # cards don't co-occur. assume 1 co-occurrence for calculating logarithm
        ab_freq = 1

    # get b-card fequency
    b_set = False
    b_freq = 0
    if b in lists['non_commander']: # there can't be 2 commanders generally
        b_freq = lists['non_commander'][b]['total']
        b_set = True
    if not b_set: # need to query the API for a data
        b_data = None
        while b_data is None:
            b_data = request_json(b,False)
        b_freq = b_data['container']['json_dict']['card']['num_decks']

    ratio = ab_freq**2/(a_freq*b_freq) # squaring the numerator gives better spread
    return math.log(ratio)

def mean (l):
    return sum(l)/len(l)

def evaluate_deck(commander, deck, lists):
    commander_sim = []
    co_card_sim = []
    for i in range(len(deck)):
        card = deck[i]
        commander_sim += synergy(commander,card,lists, a_is_commander=True)
        card_sim = []
        for j in range(len(deck)):
            if i == j: # ignore synergy with itself
                continue
            b = deck[j]
            card_sim.append(synergy(card, b, lists))
        co_card_sim.append(mean(card_sim))
    return mean(commander_sim), mean(co_card_sim)


def main():
    with open(CARDLISTS_PATH, 'rb') as f:
        comm_lists = pickle.load(f)
    commander = ... # TODO: PARSE THROUGH DECKS
    deck = ...
    return evaluate_deck(commander, deck, lists)

if __name__ == 'main':
    ...
    # Set up command-line arguments parser
    parser = argparse.ArgumentParser()

    # Add arguments
    parser.add_argument(...) # TODO: SET UP ARGUMENTS TO IDENTIFY DECK

    args = parser.parse_args()

    main(...)

