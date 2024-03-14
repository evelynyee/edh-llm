from power_calculator import calculate_power
import os
import pandas as pd
import pickle
from scrape_cardlists import DATA_PATH
BASE_PATH = os.path.join(DATA_PATH, "decks", "baseline.pkl")
BASE_PWR_PATH = os.path.join(DATA_PATH, "decks", "cos_sim")
MANUAL_PATH = os.path.join(DATA_PATH, "decks", "manual.pkl")
MANUAL_SAVE = os.path.join(DATA_PATH, "decks", "manual_rand")
EDH_SAVE = os.path.join(DATA_PATH, "decks", "edhrec")


def load_data(fp):
    with open(fp, "rb") as f:
        data = pickle.load(f)
    return data

manual = load_data(MANUAL_PATH)

for col in manual:
        cmdr_f = "".join(x for x in col if x.isalnum()) + ".txt"        
        with open(os.path.join(MANUAL_SAVE, cmdr_f), "w") as f:
            f.write(f"1 {col}\n")
            for row in manual[col].sample(63):
                f.write(f"1 {row}\n")
        with open(os.path.join(MANUAL_SAVE, cmdr_f), "a") as f:
            f.write(str(calculate_power(os.path.join(MANUAL_SAVE, cmdr_f))))