import os
import pickle
import numpy as np
import pandas as pd
from nltk.corpus import stopwords
from string import punctuation
from nltk.tokenize import word_tokenize
from sklearn.preprocessing import MinMaxScaler
from gensim.models import Word2Vec

from baseline_decks import baseline
from manual_decks import manual
from selection import build_deck
from power_calculator import calculate_power
from scrape_cardlists import DATA_PATH

CARDS_PATH = os.path.join(DATA_PATH, "cards_unique.pkl")
COMMANDERS_PATH = os.path.join(DATA_PATH, "commanders.pkl")
BASE_PATH = os.path.join(DATA_PATH, "decks", "baseline.pkl")
BASE_PWR_PATH = os.path.join(DATA_PATH, "decks", "baseline")
MANUAL_PATH = os.path.join(DATA_PATH, "decks", "manual.pkl")
BUILT_PATH = os.path.join(DATA_PATH, "built")
POWER_PATH = os.path.join(BUILT_PATH, "power")

def load_data(fp):
    with open(fp, "rb") as f:
        data = pickle.load(f)
    return data

def tokenize(text):
    to_remove = stopwords.words("english")+list(punctuation)
    return [x for x in word_tokenize(text.lower()) if x not in to_remove]

def clean_data(cards, commanders):
    cards_clean = cards.loc[cards["text"].apply(lambda x: not (isinstance(x, float) and np.isnan(x))), ["name", "text", "colorIdentity", "keywords", "type"]]
    cards_clean["color"] = cards_clean["colorIdentity"].str.split(", ")
    # tokenize text
    cards_clean["tokenized"] = cards_clean["text"].apply(tokenize)
    # normalized text length
    cards_clean["textLength"] = cards_clean["text"].str.len()
    cards_clean["textLength"] = MinMaxScaler().fit_transform(cards_clean[["textLength"]])
    # keyword list
    cards_clean["keyword_list"] = cards_clean["keywords"].str.split(", ")

    card_texts = cards_clean.loc[~cards_clean["name"].isin(commanders["valid"])]
    commander_texts = cards_clean.loc[cards_clean["name"].isin(commanders["valid"])]

    return cards_clean, commander_texts, card_texts

def train_model(cards_clean):
    return Word2Vec(sentences=cards_clean["tokenized"])

def save_decks(results_df, fp):
    # pickle.dump(results_df, fp, pickle.HIGHEST_PROTOCOL)

    all_decks = pd.read_pickle(BASE_PATH)
    for col in all_decks:
        cmdr_f = "".join(x for x in col if x.isalnum()) + ".txt"        
        with open(os.path.join(BASE_PWR_PATH, cmdr_f), "w") as f:
            f.write(f"1 {col}\n")
            for row in all_decks[col]:
                f.write(f"1 {row}\n")
        with open(os.path.join(BASE_PWR_PATH, cmdr_f), "a") as f:
            f.write(str(calculate_power(os.path.join(BASE_PWR_PATH, cmdr_f))))
        

def build_decks(commander_texts):
    for commander in commander_texts["name"]:
        build_deck(commander)

def evaluate_decks(commander_texts):
    for commander in commander_texts["name"]:
        cmdr_f = "".join(x for x in commander if x.isalnum()) + ".txt"
        pickle.dump(calculate_power(os.path.join(BUILT_PATH, cmdr_f)), os.path.join(POWER_PATH, cmdr_f))


def main():
    # cards = load_data(CARDS_PATH)
    # commanders = load_data(COMMANDERS_PATH)

    # cards_clean, commander_texts, card_texts = clean_data(cards, commanders)
    
    #model = train_model(cards_clean)

    #results_base, results_base_all = baseline(card_texts, commander_texts, model)
    #results_manual = manual(card_texts, commander_texts, model, results_base_all)
    save_decks("results_base", BASE_PATH)
    #save_decks(results_manual, MANUAL_PATH)

    # build_decks(commander_texts)

    # evaluate_decks(commander_texts)

if __name__ == "__main__":
    main()
