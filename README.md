# Pol-Spider 🕷️

This repository provides translation of [Spider](https://yale-lily.github.io/spider), [CoSQL](https://yale-lily.github.io/cosql), [SParC](https://yale-lily.github.io/sparc), [Spider-DK](https://github.com/ygan/Spider-DK), [Spider-Syn](https://github.com/ygan/Spider-Syn) datasets in multiple variants (with / without schema translation; with / without Polish characters) and code for some experiments.

📄 Associated master thesis: [download link](https://github.com/klima7/Master-Thesis/releases/download/submit/master-thesis.pdf).

## Ready datasets
Polish translations are ready to download from [Hugging Face Datasets](https://huggingface.co/datasets/klima7/Pol-Spider/tree/main) 🤗

## Datasets synthesis

Setup environment:
```bash
# clone repository
https://github.com/klima7/Polish-Spider

# create environment
conda create -n pol-spider python=3.19
conda activate pol-spider
pip install -r requirements.txt

# download spacy model
python -m spacy download xx_sent_ud_sm
```

Example dataset synthesis - synthesize dataset named `pol-spider-en`, which is based on samples from `spider`. Translate questions to polish. Apply `context-curated` translation to schema names. Translate strings in SQL queries to polish.
```bash
python datasets/scripts/synthesize.py spider pol-spider-en \
  --question-lang pl \
  --schema-translation context-curated \
  --query-lang pl \
  --with-db
```

Joining datasets - create `pol-spider` dataset by joining `pol-spider-en` and `pol-spider-pl`:
```bash
python datasets/scripts/join.py pol-spider pol-spider-en pol-spider-pl
```


## Experiments

## App
