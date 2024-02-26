from sklearn.metrics.pairwise import cosine_similarity

def manual(card_texts, commander_texts, model, results_base_all):
    results_manual_all = {}
    results_manual_keywords_all = {}
    for idx, row in commander_texts.iterrows():
        scores_all = []
        scores_keywords = []
        for card_idx, card_row in card_texts.iterrows():
            # null-color cards can go into any deck
            # null-color commanders can only take null-color cards
            if (not isinstance(card_row["color"], list)) or ((isinstance(row["color"], list)) and (all([x in card_row["color"] for x in row["color"]]))):
                # TODO add more manual features
                commander_embedding = [[row["textLength"]]]
                card_embedding = [[card_row["textLength"]]]
                scores_all.append((cosine_similarity(commander_embedding, card_embedding)[0][0], card_row["name"]))
                # checks for presence of any keywords
                if isinstance(row["keyword_list"], list) and isinstance(card_row["keyword_list"], list):
                    scores_keywords.append((model.wv.n_similarity(row["keyword_list"], card_row["keyword_list"]), card_row["name"]))
                else:
                    scores_keywords.append((0, card_row["name"]))
        results_manual_all[row["name"]] = [x[1] for x in sorted(scores_all)[::-1]]
        results_manual_keywords_all[row["name"]] = [x[1] for x in sorted(scores_keywords)[::-1]]
    
    # aggregates baseline and manual
    results_manual = {}
    for key, vals in results_base_all.items():
        results_index = []
        for val in vals:
            index_sum = results_base_all[key].index(val) + results_manual_all[key].index(val) + results_manual_keywords_all[key].index(val)
            results_index.append((index_sum, val))
        results_manual[key] = [x[1] for x in sorted(results_index)[:500]]
    
    return results_manual
