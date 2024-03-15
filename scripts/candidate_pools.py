"""
Generate candidate pools and decks for cos_sim and manual decks.
"""

import os
import pickle
import numpy as np
import pandas as pd
from nltk.corpus import stopwords
from string import punctuation
from nltk.tokenize import word_tokenize
from sklearn.preprocessing import MinMaxScaler
from gensim.models import Word2Vec

from candidate_utils import cos_sim, manual
from selection import build_deck
from power_calculator import calculate_power
from scrape_cardlists import DATA_PATH

CARDS_PATH = os.path.join(DATA_PATH, "cards_unique.pkl")
COMMANDERS_PATH = os.path.join(DATA_PATH, "commanders.pkl")
BASE_PATH = os.path.join(DATA_PATH, "decks", "cos_sim.pkl")
BASE_PWR_PATH = os.path.join(DATA_PATH, "decks", "cos_sim")
MANUAL_PATH = os.path.join(DATA_PATH, "decks", "manual.pkl")
BUILT_PATH = os.path.join(DATA_PATH, "decks",'edh-llm')
POWER_PATH = os.path.join(BUILT_PATH, "power")

def load_data(fp):
    """
    Reads in data.

    :param fp: filepath of data stored in pickle
    :returns: data stored in pickle
    """
    with open(fp, "rb") as f:
        data = pickle.load(f)
    return data

def tokenize(text):
    """
    Tokenizes text.

    :param text: text to tokenize
    :returns: tokenized text
    """
    to_remove = stopwords.words("english")+list(punctuation)
    return [x for x in word_tokenize(text.lower()) if x not in to_remove]

def clean_data(cards, commanders):
    """
    Performs multiple transformations on data, such as filtering, tokenizing text, and extracting keywords.

    :param cards: DataFrame containing information of each non-commander card, such as name, text, and color
    :param commanders: DataFrame containing information of each commander card, such as name, text, and color
    :returns: tuple containing all cleaned data, cleaned non-commander card data, and cleaned commander data
    """
    # filtering out non-legal cards in commander
    legal = pd.read_csv('../data/cardLegalities.csv').loc[:,['commander', 'uuid']]
    cards = cards.merge(legal,on='uuid')
    cards = cards[cards['commander'] == 'Legal']

    cards_clean = cards.loc[cards["text"].apply(lambda x: not (isinstance(x, float) and np.isnan(x))), ["name", "text", "colorIdentity", "keywords", "type"]]
    cards_clean["color"] = cards_clean["colorIdentity"].str.split(", ")
    # tokenize text
    cards_clean["tokenized"] = cards_clean["text"].apply(tokenize)
    # normalized text length
    cards_clean["textLength"] = cards_clean["text"].str.len()
    cards_clean["textLength"] = MinMaxScaler().fit_transform(cards_clean[["textLength"]])
    # keyword list
    cards_clean["keyword_list"] = cards_clean["keywords"].str.split(", ")

    card_texts = cards_clean.loc[~cards_clean["name"].isin(commanders["test"])]
    commander_texts = cards_clean.loc[cards_clean["name"].isin(commanders["test"])]

    return cards_clean, commander_texts, card_texts

def train_model(cards_clean):
    """
    Trains Word2Vec model on card text.

    :param cards_clean: cleaned DataFrame containing information on all cards
    :returns: trained Word2Vec model
    """
    return Word2Vec(sentences=cards_clean["tokenized"])

def save_decks(results_df, fp):
    """
    Saves decks to pickles.

    :param results_df: decks to save
    :param fp: filepath to save decks to
    """
    pd.DataFrame(results_df).to_pickle(fp)
    #pickle.dump(results_df, fp, pickle.HIGHEST_PROTOCOL)
    #results_df.to_pickle(fp)
    #all_decks = pd.read_pickle(BASE_PATH)
    #for col in all_decks:
    #    cmdr_f = "".join(x for x in col if x.isalnum()) + ".txt"
    #    with open(os.path.join(BASE_PWR_PATH, cmdr_f), "w") as f:
    #        f.write(f"1 {col}\n")
    #        for row in all_decks[col]:
    #            f.write(f"1 {row}\n")
    #    with open(os.path.join(BASE_PWR_PATH, cmdr_f), "a") as f:
    #        f.write(str(calculate_power(os.path.join(BASE_PWR_PATH, cmdr_f))))


def build_decks(commander_texts):
    """
    Builds deck for each commander

    :param commander_texts: cleaned DataFrame containing information of each commander, such as name, text, and color
    """
    for commander in commander_texts["name"]:
        build_deck(commander)

def evaluate_decks(commander_texts):
    """
    Evaluates deck for each commander

    :param commander_texts: cleaned DataFrame containing information of each commander, such as name, text, and color
    """
    for commander in commander_texts["name"]:
        cmdr_f = "".join(x for x in commander if x.isalnum()) + ".txt"
        pickle.dump(calculate_power(os.path.join(BUILT_PATH, cmdr_f)), os.path.join(POWER_PATH, cmdr_f))


def main():
    """
    Builds and evaluates cos_sim and manually created decks.
    """
    cards = load_data(CARDS_PATH)
    commanders = load_data(COMMANDERS_PATH)

    cards_clean, commander_texts, card_texts = clean_data(cards, commanders)

    model = train_model(cards_clean)

    results_base, results_base_all = cos_sim(card_texts, commander_texts, model)
    results_manual = manual(card_texts, commander_texts, model, results_base_all)
    save_decks(results_base, BASE_PATH)
    save_decks(results_manual, MANUAL_PATH)

    build_decks(commander_texts)

    evaluate_decks(commander_texts)

if __name__ == "__main__":
    main()