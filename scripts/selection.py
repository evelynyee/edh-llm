from openai import OpenAI
import pickle
from power_calculator import calculate_power
import os
import time

def load_data(fp):
    with open(fp, "rb") as f:
        data = pickle.load(f)
    return data

data = load_data(os.path.abspath("data/decks/manual.pkl"))

cmdr = 'Elenda, the Dusk Rose'
pool = set(data[cmdr])      
target_power = calculate_power('data/test_deck.txt')
cur_power = 0
client = OpenAI(api_key='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')
start_time = time.time()
with open(os.path.abspath("data/temp_deck.txt"), "a+") as file:
    file.write("1 " + cmdr + "\n")
    file.seek(0)
    while len(file.readlines()) <= 100:
        file.seek(0)
        cur_deck = file.readlines()
        print(cur_deck)
        completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are building a commander deck for magic the gathering. You will be given a pool of already selected cards, a candidate pool, some hueristics of the cards already selected as well as a target hueristic score. Select five the cards from the candidate pool that will move the current hueristic score toward the target score. Return simply the names of the cards you have selected, separated by semi-colons"},
            {"role": "user", "content": \
            "Selected: " + '; '.join(cur_deck) +\
            "Candidate Pool: " + '; '.join(pool) + \
            "Current Power: " + str(cur_power) + \
            "Target Power: " + str(target_power)}
        ]
        )

        picked = completion.choices[0].message.content.split('; ')

        for card in picked:
            if card in pool:
                pool.remove(card)
                file.write("1 " + card + "\n")
            else:
                print('failed to find ' + card)
        file.seek(0)
        if len(file.readlines()) > 6:
            cur_power = calculate_power('data/temp_deck.txt')
        print('Time Elapsed: ' + str(time.time()-start_time))
        print('Adding: ' + picked)
        print(cur_power)
        file.seek(0)

os.rename('data/temp_deck.txt', 'data/'+"".join(x for x in cmdr if x.isalnum())+'.txt')
