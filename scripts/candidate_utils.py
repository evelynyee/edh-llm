"""
Utilities to generate candidate pools, using Word2Vec and manual features.
"""
from sklearn.metrics.pairwise import cosine_similarity
import os

LANDS = {"W": "Plains",
         "U": "Island",
         "B": "Swamp",
         "R": "Mountain",
         "G": "Forest"}

def cos_sim(card_texts, commander_texts, model):
    """
    Creates baseline decks based on cosine similarity between commander text and card text.

    :param card_texts: cleaned DataFrame containing information of each non-commander card, such as name, text, and color
    :param commander_texts: cleaned DataFrame containing information of each commander, such as name, text, and color
    :param model: Word2Vec model that has been trained on all card texts
    :returns: tuple containing a dict of key:value pairs of commander:99 card deck, and a dict of key:value pairs of commander:all cards, ranked by similarity
    """
    results_base_all = {}
    results_base = {}
    for idx, row in commander_texts.iterrows():
        scores = []
        for card_idx, card_row in card_texts.iterrows():
            # null-color cards can go into any deck
            # null-color commanders can only take null-color cards
            if (not isinstance(card_row["color"], list)) or ((isinstance(row["color"], list)) and (all([x in row["color"] for x in card_row["color"]]))):
                scores.append((model.wv.n_similarity(row["tokenized"], card_row["tokenized"]), card_row["name"], card_row["type"]))
        # sorts scores
        sorted_scores = sorted(scores)[::-1]
        results_base_all[row["name"]] = [x[1] for x in sorted_scores]

        # 36 land per deck
        base_land = []
        base_nonland = []
        for score in sorted_scores:
            if len(base_nonland) < 63:
                if score[2] == "Land":
                    if len(base_land) < 36:
                        base_land.append(score[1])
                else:
                    base_nonland.append(score[1])
            else:
                break
        # adds appropriate lands
        commander_colors = row["color"]
        if isinstance(commander_colors, list):
            for i in range(36 - len(base_land)):
                base_land.append(LANDS[commander_colors[i % len(commander_colors)]])
        else:
            for i in range(36 - len(base_land)):
                base_land.append("Wastes")
        results_base[row["name"]] = base_land + base_nonland

    return results_base, results_base_all

def manual(card_texts, commander_texts, model, results_base_all):
    """
    Creates manual decks based on cosine similarity between commander text and card text, keywords, and manual features.

    :param card_texts: cleaned DataFrame containing information of each non-commander card, such as name, text, and color
    :param commander_texts: cleaned DataFrame containing information of each commander, such as name, text, and color
    :param model: Word2Vec model that has been trained on all card texts
    :param results_base_all: dict of key:value pairs of commander:all cards, ranked by similarity
    :returns: tuple containing a dict of key:value pairs of commander:800 card candidate pool
    """
    # reads in staples
    staples = {}
    with open(os.path.abspath('../data/staples.txt'), 'r') as f:
        staple_pool = [s.rstrip() for s in f.readlines()]

    results_manual_all = {}
    results_manual_keywords_all = {}
    for idx, row in commander_texts.iterrows():
        scores_all = []
        scores_keywords = []
        staples[row['name']] = []
        for card_idx, card_row in card_texts.iterrows():
            # null-color cards can go into any deck
            # null-color commanders can only take null-color cards
            if (not isinstance(card_row["color"], list)) or ((isinstance(row["color"], list)) and (all([x in row["color"] for x in card_row["color"]]))):
                commander_embedding = [[row["textLength"]]]
                card_embedding = [[card_row["textLength"]]]
                scores_all.append((cosine_similarity(commander_embedding, card_embedding)[0][0], card_row["name"]))
                # checks for presence of any keywords
                if isinstance(row["keyword_list"], list) and isinstance(card_row["keyword_list"], list):
                    scores_keywords.append((model.wv.n_similarity(row["keyword_list"], card_row["keyword_list"]), card_row["name"]))
                else:
                    scores_keywords.append((0, card_row["name"]))
                    # checking for inclusion in manual staple pool
                    if card_row['name'] in staple_pool:
                        staples[row['name']].append(card_row['name'])
        # sorts scores
        results_manual_all[row["name"]] = [x[1] for x in sorted(scores_all)[::-1]]
        results_manual_keywords_all[row["name"]] = [x[1] for x in sorted(scores_keywords)[::-1]]



    # aggregates cos_sim and manual
    results_manual = {}
    for key, vals in results_base_all.items():
        results_index = []
        # sums up all rankings
        for val in vals:
            index_sum = results_base_all[key].index(val) + results_manual_all[key].index(val) + results_manual_keywords_all[key].index(val)
            results_index.append((index_sum, val))
        # returns top 500 scoring cards plus color-valid staples
        results_manual[key] = [x[1] for x in sorted(results_index)[:500]] + staples[key][:min(len(v) for v in staples.values())]

    return results_manual
