# Abstract

The physical condition is one of the most important criteria contributing to the collector coin’s market
value. Coin grading requires a deep knowledge of the domain. Certificated grade and estimation of the
wear state of the coin made by an expert is the additional cost included in the price of the coin.
This work examines the “Bag of Visual Words (BOVW)” algorithm based on image analysis and
machine learning algorithms. For that purpose, the procedure of processing the coin is proposed, and
BOVW is used for performing wear state grading of the coin based on features extracted from digital
images of the coin. The algorithm was trained on the data for the chosen type of coin, gained from the
two biggest polish numismatic auction houses.

# Instalation

## MacOs

1. Install chromedriver via homebrew

    ```sh
    brew install --cask chromedriver
    ```

2. Go to directory with chromedriver and remove chromedriver from quarantine

    ```sh
    cd /usr/local/Caskroom/chromedriver/<version-of-chromedriver>/
    xattr -d com.apple.quarantine chromedriver
    ```

# Run

```sh
python3 -m src.0_scraper_pipeline "Sztandar 1930"
```

```sh
python3 -m src.2_parser_pipeline
```
