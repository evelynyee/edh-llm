# checkpoint code
# TODO: clean code, modify tokenization?, look into validity of results

import pickle
from nltk.corpus import stopwords
from string import punctuation
from nltk.tokenize import word_tokenize
from gensim.models import Word2Vec
import numpy as np
import pandas as pd


with open(f"../data/cards.pkl", "rb") as f:
    cards = pickle.load(f).drop_duplicates(subset=['name', 'colorIdentity', 'text']).reset_index(drop=True)
with open(f"../data/commanders.pkl", "rb") as f:
    commanders = pickle.load(f)


def tokenize(text):
    to_remove = stopwords.words("english")+list(punctuation)
    return [x for x in word_tokenize(text.lower()) if x not in to_remove]


cards_clean = cards.loc[cards["text"].apply(lambda x: not (isinstance(x, float) and np.isnan(x))), ["name", "text"]]
cards_clean["tokenized"] = cards_clean["text"].apply(tokenize)

commander_texts = cards_clean.loc[cards_clean["name"].isin(commanders["valid"]), ["name", "text", "tokenized"]]

card_texts = cards_clean.loc[~cards_clean["name"].isin(commanders["valid"]), ["name", "text", "tokenized"]]


model = Word2Vec(sentences=cards_clean["tokenized"])


results = {}
for idx, row in commander_texts.iterrows():
    scores = []
    for card_idx, card_row in card_texts.iterrows():
        scores.append((model.wv.n_similarity(row["tokenized"], card_row["tokenized"]), card_row["name"]))
    results[row["name"]] = [x[1] for x in sorted(scores)[-100:]]


print(pd.DataFrame(results).to_string())
