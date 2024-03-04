# EDH-LLM: Using NLP techniques to build card game decks
*Theodore Hui, Linus Lin, and Evelyn Yee*

*Mentor: Jingbo Shang*

## About our project
TODO: THE ABSTRACT BUT LESS TECHNICAL

## What is EDH?
TODO: DESCRIPTION OF MAGIC THE GATHERING AND THE EDH FORMAT

### The deck building problem
TODO: DESCRIBE THE PROBLEM

## Our pipeline
![A diagram demonstrating our pipeline, from Magic the Gathering cards and a specified commander to the final deck suggestion.](pipeline_diagram.png)

TODO: HIGH-LEVEL DESCRIPTION OF OUR PIPELINE
1. TODO
2. TODO

### Card embeddings
TODO: HIGH-LEVEL DESCRIPTION OF OUR DUAL EMBEDDING PROCESS

### Using ChatGPT
TODO: HIGH-LEVEL DESCRIPTION OF HOW/WHY WE USED CHATGPT

## Evaluation

### Baselines
We evaluate our pipeline against three alternative methods for building EDH Decks:
- **Popularity Baseline:** Select the top cards which are most frequently played with the selected Commander, according to historical play data from EDHRec1
- **Embedding-only Baseline:** Gather the top cards from each vector-embedding candidate pool, without any reranking by GPT-3.5.
- **Basic Prompt Baseline:** TODO: DESCRIPTION

### Synergy
![Synergy Formula](synergy-formula.png)

We estimate the synergy between a pair of cards through a Bayesian probability measure, based on card co-occurrence in decklist data from EDHRec.1 For each deck, we record the average synergy over all pairs of non-basic cards as well as the Commander synergy between each non-commander card and the commander.

![INSERT SYNERGY RESULTS TABLES/GRAPHS]()

### Power Level
![Power Level Formula](power-formula.png)

We use [an online EDH deck power calculator](https://edhpowercalculator.com/) for evaluating the power level of an EDH deck based on the distribution of functional card types during gameplay. A powerful deck should have a balance of card draw, interaction, and speed for a low cost. The original formula was created by the blogger [Disciple of the Vault](discipleofthevault.com/2020/11/18/my-edh-power-level-formula/).

![INSERT POWER RESULTS TABLES/GRAPHS]()

### Subjective Evaluation
Additionally, we perform some human evaluation to assess the subjective, domain-informed performance of our generated decks.

![INSERT HUMAN RESULTS TABLES/GRAPHS]()

## Conclusion
TODO: CONCLUSION

## Contact
- Theodore Hui: tchui@ucsd.edu
- Linus Lin: l6lin@ucsd.edu
- Evelyn Yee: eyee@ucsd.edu
- Jingbo Shang: jshang@ucsd.edu
![Halıcıoğlu Data Science Institute.](hdsi-blue-gold.png)


