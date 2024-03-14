# EDH-LLM: Using NLP techniques to build card game decks
*Theodore Hui, Linus Lin, and Evelyn Yee*

*Mentor: Jingbo Shang*

## About our project
In our project, we propose a novel system for generating playable decks for the card game, ”Magic: The Gathering,” in the commander format (also known as EDH; Elder Dragon Highlander). In this format, decks consist of 1 Commander card, and 99 non-Commander cards. This task combines hard and soft restrictions, maximizing the validity, playability, and power of a deck, in addition to an issue of scale, as there are thousands of possible cards, leading to over 10285 total possible decks. To address the holistic demands of this deck-building task in this large search space, our system features Natural Language Processing (NLP) techniques, alongside a Large Language Model (LLM) in the loop. In this way, we extract the maximum utility from the text data provided with each card. Alongside an existing formula for evaluating the power level of EDH decks, we also propose a new, count-based metric for predicting card synergy based on unlabeled historical play data.

## What is EDH?
Magic the Gathering is a deck-building card game where players collect cards and assemble custom decks to play against each other. The Elder Dragon Highlander (EDH) format is loosely structured for deck-building; players must select a Commander card (see below) to lead 99 other cards in a 1v1v1v1 last-man-standing format.

<img src="AtraxaPraetorsVoice033__72510.jpeg" alt="Commander card" width="300" style="text-align:center;"/>

Sample commander card: Atraxa, Praetors' Voice

### The deck building problem
Building a successful deck necessitates the following considerations with varying levels of subjectivity:
1. Hard Restrictions:

    • The commander must be a Legendary Creature. There are thousands of Legendary Creature cards.

    • The other 99 cards in the deck must fit into the color typing of the commander.

2. Soft Restrictions:

    • Synergies: Cards in a deck must play well with each other. This can be expressed in many ways, including typal synergies, playstyle archetypes, and combos.

    • Power Curve: Decks must strike a balance between three main archetypes of cards; card draw, mana generation, and gameplan cards must be evenly balanced in a deck to allow a smooth gameplay experience. Missing a turn due to lack of cards or mana, or failing to execute a gameplan are all risks that can be minimized by good deck composition.

    • Rule Zero: Decks must be fun to play with and play against. This can be achieved by building a deck that is, on average, of comparable speed/strength to other decks in the playgroup.

## Our pipeline
![A diagram demonstrating our pipeline, from Magic the Gathering cards and a specified commander to the final deck suggestion.](pipeline_diagram.png)

1. Gather database of all Magic: The Gathering cards
2. Convert each card's text to its vector representation
3. Create another vector of each card's various features
4. Use these vectors to create a candidate pool, and add staple cards to it
5. Given a commander, prompt ChatGPT to select appropriate cards for the final deck.
6. Repeat step 5 until a deck of 99 cards is reached.

### Card embeddings
We use Word2Vec, a NLP tool, to convert card text into its vector representation. We calculate the similarity between the specified commander and each card, ranking each pair's similarity. Next, we utilize the same strategy again, but for features instead of text. With each card's feature vector representation, we can calculate the similarity between the commander and each card, again, ranking each pair's similarity. Finally, we aggregate both rankings to create one final, joined ranking.

### Using ChatGPT
With our data consisting primarily of text, NLP tools, such as ChatGPT, can help us find similarities between cards and significantly reduce the search space. ChatGPT has significant potential to help us narrow down the cards even further, as it has been trained on several hundred gigabytes of text, allowing us to indirectly access large amounts of data training with strategic prompting. ChatGPT will allow us to semi-automatically group cards together through the use of guided prompts. This can either be done through the use of iterative prompts, asking ChatGPT to pick which of two cards is most similar to a cluster, or simply iteratively prompting ChatGPT to the add single most similar document to the cluster.

## Evaluation

### Baselines
We evaluate our pipeline against three alternative methods for building EDH Decks:
- **Popularity Baseline:** Select the top cards which are most frequently played with the selected Commander, according to historical play data from EDHRec1
- **Embedding-only Baseline:** Gather the top cards from each vector-embedding candidate pool, without any reranking by GPT-3.5.

### Synergy
![Synergy Formula](synergy-formula.png)

We estimate the synergy between a pair of cards through a Bayesian probability measure, based on card co-occurrence in decklist data from EDHRec.1 For each deck, we record the average synergy over all pairs of non-basic cards as well as the Commander synergy between each non-commander card and the commander.

![TODO: INSERT SYNERGY RESULTS TABLES/GRAPHS]()

### Power Level
![Power Level Formula](power-formula.png)

We use [an online EDH deck power calculator](https://edhpowercalculator.com/) for evaluating the power level of an EDH deck based on the distribution of functional card types during gameplay. A powerful deck should have a balance of card draw, interaction, and speed for a low cost. The original formula was created by the blogger [Disciple of the Vault](discipleofthevault.com/2020/11/18/my-edh-power-level-formula/).

![TODO: INSERT POWER RESULTS TABLES/GRAPHS]()

### Subjective Evaluation
Additionally, we perform some human evaluation to assess the subjective, domain-informed performance of our generated decks.

![TODO: INSERT HUMAN RESULTS TABLES/GRAPHS]()

## Conclusion
TODO: CONCLUSION

## Contact
- Theodore Hui: tchui@ucsd.edu
- Linus Lin: l6lin@ucsd.edu
- Evelyn Yee: eyee@ucsd.edu
- Jingbo Shang: jshang@ucsd.edu
![Halıcıoğlu Data Science Institute.](hdsi-blue-gold.png)


