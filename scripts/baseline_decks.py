LANDS = {"W": "Plains",
         "U": "Island",
         "B": "Swamp",
         "R": "Mountain",
         "G": "Forest"}

def baseline(card_texts, commander_texts, model):
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
