# checkpoint code
# TODO: clean code, modify tokenization?, look into validity of results

import pickle

from nltk.corpus import stopwords
from string import punctuation
from nltk.tokenize import word_tokenize
from gensim.models import Word2Vec
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LogisticRegression

import numpy as np
import pandas as pd


with open(f"../data/cards.pkl", "rb") as f:
    cards = pickle.load(f).drop_duplicates(subset=['name', 'colorIdentity', 'text']).reset_index(drop=True)
# with open(f"../data/cards_unique.pkl", "rb") as f:
#     cards = pickle.load(f)
with open(f"../data/commanders.pkl", "rb") as f:
    commanders = pickle.load(f)
with open(f"../data/edhreclists.pkl", "rb") as f:
    lists = pickle.load(f)


def tokenize(text):
    to_remove = stopwords.words("english")+list(punctuation)
    return [x for x in word_tokenize(text.lower()) if x not in to_remove]


cards_clean = cards.loc[cards["text"].apply(lambda x: not (isinstance(x, float) and np.isnan(x))), ["name", "text", "borderColor", "keywords"]]
# one-hot encode color
cards_clean = pd.get_dummies(cards_clean, columns=["borderColor"])
colors = [col for col in cards_clean.columns if col.startswith("borderColor")]
# tokenize text
cards_clean["tokenized"] = cards_clean["text"].apply(tokenize)
# normalized text length
cards_clean["textLength"] = cards_clean["text"].str.len()
cards_clean["textLength"] = MinMaxScaler().fit_transform(cards_clean[["textLength"]])
# keyword list
cards_clean["keyword_list"] = cards_clean["keywords"].str.split(", ")

commander_texts = cards_clean.loc[cards_clean["name"].isin(commanders["valid"])]
card_texts = cards_clean.loc[~cards_clean["name"].isin(commanders["valid"])]


vector_size = 100
model = Word2Vec(sentences=cards_clean["tokenized"], vector_size=vector_size)


# baseline results
results_base_all = {}
results_base = {}
for idx, row in commander_texts.iterrows():
    scores = []
    for card_idx, card_row in card_texts.iterrows():
        scores.append((model.wv.n_similarity(row["tokenized"], card_row["tokenized"]), card_row["name"]))
    results_base_all[row["name"]] = [x[1] for x in sorted(scores)[::-1]]
    results_base[row["name"]] = results_base_all[row["name"]][:99]


# manual features
results_manual_all = {}
results_manual_keywords_all = {}
for idx, row in commander_texts.iterrows():
    scores_all = []
    scores_keywords = []
    for card_idx, card_row in card_texts.iterrows():
        # TODO manual features
        commander_embedding = [list(row[colors]) + [row["textLength"]]]
        card_embedding = [list(card_row[colors]) + [card_row["textLength"]]]
        # print((cosine_similarity(commander_embedding, card_embedding)[0][0], card_row["name"]))
        # stop
        scores_all.append((cosine_similarity(commander_embedding, card_embedding)[0][0], card_row["name"]))
        if isinstance(row["keyword_list"], list) and isinstance(card_row["keyword_list"], list):
            scores_keywords.append((model.wv.n_similarity(row["keyword_list"], card_row["keyword_list"]), card_row["name"]))
        else:
            scores_keywords.append((0, card_row["name"]))
    results_manual_all[row["name"]] = [x[1] for x in sorted(scores_all)[::-1]]
    results_manual_keywords_all[row["name"]] = [x[1] for x in sorted(scores_keywords)[::-1]]


# aggregates results
results_manual = {}
for key, vals in results_base_all.items():
    results_index = []
    for val in vals:
        index_sum = results_base_all[key].index(val) + results_manual_all[key].index(val) + results_manual_keywords_all[key].index(val)
        results_index.append((index_sum, val))
    results_manual[key] = [x[1] for x in sorted(results_index)[:99]]


print("Baseline:")
print(pd.DataFrame(results_base).to_string())

print("Manual features:")
print(pd.DataFrame(results_manual).to_string())
