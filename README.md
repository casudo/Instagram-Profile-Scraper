> This project is intended for educational purposes only! 

# Instagram Profile Scraper
Yet another Instagram profile scraper to gather followers/following, post count and bio from Instagram accounts.
Supports Discord notifications on changes. Uses Chrome with Selenium.

## Installation
Install all requirements with:
`pip install -r requirements.txt`

You need to change the Discord webhook in the source code to your own webhook in order to get notifications. You can find it with `Ctrl + F` and searching for `CHANGEME`.

## Planned in future
- Docker Image
- Error handling for wrong credentials
- Error handling for wrong 2FA code
- Automatically redo scraping when suggested profiles are found

## Usage
You shouldn't enter more than four users due to some regulations from Instagram. The scraper might stop working correctly when entering more.

`run_local.py`: Works on Windows as long as Chrome is installed. GUI is visible.
`run_docker.py`: Works on Linux. GUI is not visible. **(Planned in future)**

## Known issues
When opening followers on the web, Instagram doesn't load all accounts correctly. Let's say the account you want to scrape has 150 followers. On the first run, it will scrape 142 followers, on the second run 138, then 134. 

Sometimes it loads "username1" as follower in two runs and on the third run the account somehow doesn't appear in the followers anymore. 

This "bug" makes the comparisons between runs unpredictable, so caution is still advised here.

> Following works perfectly tho.