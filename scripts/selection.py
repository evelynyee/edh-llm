from openai import OpenAI
import pickle
from scripts.power_calculator import calculate_power
import os
import time

def load_data(fp):
    with open(fp, "rb") as f:
        data = pickle.load(f)
    return data

data = load_data(os.path.abspath("../data/decks/manual.pkl"))
def build_deck(cmdr, target_power = {'overall': 9, 'cmc': 1.74, 'ramp': 18, 'draw': 20, 'interaction': 14}):
    """
    Creates a deck for a commander based on the candidate pools targeting the passed in power level
    
    Parameters:
    - cmdr: commander name
    - target_power: dictionary with 'overall', 'cmc', 'ramp', 'draw', 'interaction' stats

    Returns:
    None, writes deck to data/decks/gpt/{cmdr}.txt 
    """
    pool = set(data[cmdr])      
    #target_power = calculate_power('../data/test_deck.txt')
    cur_power = 0
    client = OpenAI()
    start_time = time.time()

    ### ChatGPT call
    with open(os.path.abspath('../data/decks/gpt/'+"".join(x for x in cmdr if x.isalnum())+'.txt'), "a+") as file:
        file.seek(0)
        if (len(file.readlines()) == 0):
            file.write("1 " + cmdr + "\n")
        file.seek(0)
        while len(file.readlines()) <= 63:
            file.seek(0)
            cur_deck = file.readlines()
            print(cur_deck)
            try:
                completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are building a commander deck for magic the gathering. You will be given a pool of already selected cards, a candidate pool, some hueristics of the cards already selected as well as a target hueristic score. Select five the cards from the candidate pool that will move the current hueristic score toward the target score. For example, if the target ramp score is 10 and the current score is 3, pick cards that will aid with mana generation. Return simply the names of the cards you have selected, separated by semi-colons. Do not deviate from the formatting specified."},
                    {"role": "user", "content": \
                    "Selected: " + '; '.join(cur_deck) +\
                    "Candidate Pool: " + '; '.join(pool) + \
                    "Current Power: " + str(cur_power) + \
                    "Target Power: " + str(target_power)}
                ]
                )
            except:
                time.sleep(60)
                build_deck(cmdr)
            
            #Remove picked cards from pool and add to deck
            picked = completion.choices[0].message.content.split('; ')
            for card in picked:
                if card in pool:
                    pool.remove(card)
                    file.write("1 " + card + "\n")
                else:
                    print('failed to find ' + card)
            file.seek(0)

            #Update current power score
            if len(file.readlines()) > 6:
                try:
                    cur_power = calculate_power(os.path.abspath('../data/decks/gpt/'+"".join(x for x in cmdr if x.isalnum())+'.txt'))
                except Exception as e:
                    print(e)
                    time.sleep(60*60)
            print('Time Elapsed: ' + str(time.time()-start_time))
            print('Adding: ' + completion.choices[0].message.content)
            print(cur_power)
            file.seek(0)
            if len(file.readlines()) >= 63:
                file.write(str(cur_power))
            file.seek(0)
