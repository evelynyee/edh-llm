from power_calculator import calculate_power
import os
import pandas as pd
import pickle
from tqdm import tqdm
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


def gen_manual_rand():
    """
    Writes manual_rand decks to folder
    """
    manual = load_data(MANUAL_PATH)

    for col in tqdm(manual):
            cmdr_f = "".join(x for x in col if x.isalnum()) + ".txt"        
            with open(os.path.join(MANUAL_SAVE, cmdr_f), "w") as f:
                f.write(f"1 {col}\n")
                for row in manual[col].sample(63):
                    f.write(f"1 {row}\n")
            with open(os.path.join(MANUAL_SAVE, cmdr_f), "a") as f:
                f.write(str(calculate_power(os.path.join(MANUAL_SAVE, cmdr_f))))

def gen_cos_sim():
    """
    Writes cos_sim decks to folder
    """
    all_decks = pd.read_pickle(BASE_PATH)
    for col in tqdm(all_decks):
        cmdr_f = "".join(x for x in col if x.isalnum()) + ".txt"        
        with open(os.path.join(BASE_PWR_PATH, cmdr_f), "w") as f:
            f.write(f"1 {col}\n")
            for row in all_decks[col]:
                f.write(f"1 {row}\n")
        with open(os.path.join(BASE_PWR_PATH, cmdr_f), "a") as f:
            f.write(str(calculate_power(os.path.join(BASE_PWR_PATH, cmdr_f))))

def gen_edhrec():
    """
    Writes edhrec decks to folder
    """
    manual = load_data(MANUAL_PATH)
    edhrec = load_data(os.path.join(DATA_PATH, "edhreclists.pkl"))
    edhrec = pd.DataFrame(edhrec)
    for commander in tqdm(edhrec[[i in manual.columns for i in edhrec.index]].index):
        cmdr_f = "".join(x for x in commander if x.isalnum()) + ".txt"
        with open(os.path.join(EDH_SAVE, cmdr_f), "w") as f:
            f.write(f"1 {commander}\n")
            for row in list(edhrec.loc[commander]['test']['cards'].keys())[:63]:
                f.write(f"1 {row}\n")
        with open(os.path.join(EDH_SAVE, cmdr_f), "a") as f:
                f.write(str(calculate_power(os.path.join(EDH_SAVE, cmdr_f))))
        #print(commander, list(edhrec.loc[commander]['valid']['cards'].keys())[:62])
        #print(list(edhrec.iloc[0]['valid']['cards'].keys())[:100])