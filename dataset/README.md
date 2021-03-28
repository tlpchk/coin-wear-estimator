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