# EDH-LLM: Using LLMs to build MtG Decks
## Data Science Capstone Project 2024
## Theodore Hui, Linus Lin, and Evelyn Yee
DSC 180 - Section B15 Group 2
Mentor: Dr. Jingbo Shang
[View our website](evelynyee.github.io/edh-llm)


## Reproduceability
### Requirements:
#### Packages:
- ast (2.0.5)
- beautifulsoup4 (4.12.2)
- gensim (4.3.2)
- matplotlib (3.8.1) (for data visualization)
- nltk (3.7)
- numpy (1.23.4)
- os (3.8.5)
- pandas (1.5.1)
- pickle (3.8.5)
- requests (2.31.0)
- seaborn (0.13.2) (for data visualization)
- selenium (4.17.2)
- sklearn (1.1.1)
- string (3.8.5)

#### Other:
- Chrome (121.0.6167) Otherwise install appropriate version of chromedriver from https://chromedriver.chromium.org/

### Instructions
All of the necessary data for our project is in the `data` folder, but if you would like to run it on commanders which we didn't select, you will have to follow this process. All scripts are in the `scripts` folder and can be run from the command line with `python3 <script name>.py`
1. Scraping EDHRec data:
    - Getting commander list: run `scrape_commanders.py`. Set the number of commanders to scrape with the `VALID` and `TEST` constants at the top of that file (corresponding to the number of commanders selected for validation and test set, 100 and 200 respectively by default). If you want to specify certain commanders instead of randomly selecting them, simply list these commanders in the `data/commanders.pkl` file.
    - Getting associated card lists: run `scrape_cardlists.py`. This will scrape all cardlists associated with the commanders in the commanders file, created above. This may take a while, depending on the number of commanders.
2. Building Word2Vec baseline decks and selecting cardlist candidate pools:
    - Run `candidate_pools.py`. This will save the baseline decks and cardlist candidate pools to the `data/decks` folder.
3. Re-ranking candidate pools:
    - TODO: HOW DOES THIS WORK?
4. Evaluating decks:
    - Synergy metric: run `synergy.py`. This has the required argument `--decktype`, which should be the name of the deck type to be evaluated (i.e. one of `cos_sim`, `edhrec`, `manual_rand`, or `edh-llm`)
    - Power Heuristic metric: import the power_calculator method and pass in filepath to deck. After 30-40 seconds it will return an overall power rating, the average CMC (converted mana cost), the amount of card draw/advantage, and the amount of interaction cards in the deck.
5. (Optional) Data exploration and visualization:
    - We provide some guidance for data exploration and visualization in the `graphs.ipynb` notebook, where you can re-generate all of our graphs and see some exploratory statistical analysis of our results.
