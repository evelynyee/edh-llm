# EDH-LLM: Using LLMs to build MtG Decks
## Data Science Capstone Project 2024
## Theodore Hui, Linus Lin, and Evelyn Yee
DSC 180 - Section B15 Group 2
Mentor: Dr. Jingbo Shang


## Reproduceability
### Requirements:
#### Packages:
- requests (2.31.0)
- beautifulsoup4 (4.12.2)
- selenium (4.17.2)
- os (3.8.5)
- pickle (3.8.5)
- numpy (1.23.4)
- pandas (1.5.1)
- nltk (3.7)
- string (3.8.5)
- sklearn (1.1.1)
- gensim (4.3.2)

#### Other:
- Chrome (121.0.6167) Otherwise install appropriate version of chromedriver from https://chromedriver.chromium.org/

### Instructions
All of the necessary data for our project is in the `data` folder, but if you would like to run it on commanders which we didn't select, you will have to follow this process. All scripts are in the `scripts` folder and can be run from the command line with `python3 <script name>.py`
1. Scraping EDHRec data:
    - Getting commander list: run `scrape_commanders.py`. Set the number of commanders to scrape with the `VALID` and `TEST` constants at the top of that file (corresponding to the number of commanders selected for validation and test set, 100 and 200 respectively by default). If you want to specify certain commanders instead of randomly selecting them, simply list these commanders in the `data/commanders.pkl` file.
    - Getting associated card lists: run `scrape_cardlists.py`. This will scrape all cardlists associated with the commanders in the commanders file, created above. This may take a while, depending on the number of commanders.
2. Building Word2Vec baseline decks and selecting cardlist candidate pools:
    - Run `pipeline.py`. This will save the baseline decks and cardlist candidate pools to the `data/decks` folder.
3. Evaluating decks:
    - Synergy metric: run `synergy.py`. This is still in progress to fit to our deck format
    - Power Heuristic metric: TODO - FILL IN REPRODUCTION INSTRUCTIONS
