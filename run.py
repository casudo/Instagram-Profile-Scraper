import time
import os
import requests

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

from webdriver_manager.chrome import ChromeDriverManager

from art import *

VERSION = "v0.1.0"

### -----------------------------------------------------------------------------------
### -----------------------------------------------------------------------------------
### -----------------------------------------------------------------------------------

def load_credentials():
    if not os.path.exists("credentials.txt"):
        return None

    with open("credentials.txt", "r") as file:
        lines = file.readlines()
        if len(lines) >= 2:
            return lines[0].strip(), lines[1].strip()

    return None


def prompt_credentials():
    username = input("Enter your Instagram email: ")
    password = input("Enter your Instagram password: ")
    save_credentials(username, password)
    return username, password


def save_credentials(username, password):
    with open("credentials.txt", "w") as file:
        file.write(f"{username}\n{password}")


def login(driver, username, password):
    # Navigate to Instagram
    driver.get("https://instagram.com/accounts/login")
    time.sleep(1)

    # Check for cookies popup
    try:
        # Desktop version
        ## decline_cookies = driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[3]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/button[2]")
        # Mobile version
        decline_cookies = driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[3]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div[3]/div[2]/button")

        decline_cookies.click()
        print("\n[INFO] Cookies have been declined.")
    except NoSuchElementException:
        pass

    # Logging in
    try:
        username_field = driver.find_element(By.CSS_SELECTOR, "input[name='username']")
        password_field = driver.find_element(By.CSS_SELECTOR, "input[name='password']")
        print("[INFO] Logging in...")

        # Clear the fields and input with the login info provided
        username_field.clear()
        username_field.send_keys(username)
        password_field.clear()
        password_field.send_keys(password)

        time.sleep(2)

        # Click submit button
        login_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
        login_button.click()
        time.sleep(5)
        ### ADD ERROR HANDLING FOR WRONG CREDENTIALS HERE

        # check for 2FA
        try:
            twofactor = driver.find_element(By.CSS_SELECTOR, "input[name='verificationCode']")

            twofactor_i = input("\nEnter your Instagram 2FA code: ")

            twofactor.clear()
            twofactor.send_keys(twofactor_i)

            confirm_button = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='button']")))
            confirm_button.click()
            time.sleep(5)
            ### ADD ERROR HANDLING FOR WRONG 2FA CODE HERE

            print("[INFO] Successfully logged in with 2FA.")
        except NoSuchElementException:
            print("[INFO] Successfully logged in without 2FA.")
    except NoSuchElementException:
        pass

    # Disable Notifications
    try:
        notifications = driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[3]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]/button[2]")
        notifications.click()
        print("[INFO] Notifications have been disabled.")
    except NoSuchElementException:
        pass

    # Get users to scrape
    users_to_scrape = input("\nEnter the Instagram usernames you want to scrape (separated by comma ONLY): ").split(",")
    for user in users_to_scrape:
        user = user.strip()
        scrape_followers(driver, user)
        scrape_following(driver, user)


def scrape_followers(driver, username):
    # Open user profile
    driver.get(f"https://www.instagram.com/{username}/")
    time.sleep(3.5)
    
    # Gather some general information about the user
    post_count = driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/div[2]/section/main/div/header/section/ul/li[1]/span/span").text
    followers_count = driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/div[2]/section/main/div/header/section/ul/li[2]/a/span/span").text
    following_count = driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/div[2]/section/main/div/header/section/ul/li[3]/a/span/span").text
    profile_bio = driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/div[2]/section/main/div/header/section/div[3]/div/span").text
    print(f"\n[INFO] --- Some info for {username} ---\n"
        f"-> Posts: {post_count}\n"
        f"-> Followers: {followers_count}\n"
        f"-> Following: {following_count}\n"
        f"-> Bio: {profile_bio}\n")
    time.sleep(1)

    # Open followers
    WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/followers')]"))).click()
    time.sleep(3)

    # Scroll through all followers
    scroll_box = driver.find_element(By.XPATH, "//div[@class='_aano']")
    time.sleep(1)
    last_ht, ht = 0, 1  # height variables
    while last_ht != ht:
        last_ht = ht
        time.sleep(2)
        ht = driver.execute_script("""
                arguments[0].scrollTo(0, arguments[0].scrollHeight);
                return arguments[0].scrollHeight; """, scroll_box)

    # Start scraping followers
    print(f"[Info] Scraping followers for {username}...")

    users = set()

    followers = driver.find_elements(By.XPATH, "//div[@class='_aano']//div[@class='x9f619 xjbqb8w x78zum5 x168nmei x13lgxp2 x5pf9jr xo71vjh x1uhb9sk x1plvlek xryxfnj x1c4vz4f x2lah0s x1q0g3np xqjyukv x1qjc9v5 x1oa3qoh x1nhvcw1']//a[contains(@href, '/')]")

    # do this to prevent suggested profiles at the end of the follower list
    try:
        driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[3]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[2]/div[2]/span")
        print("[WARN] Found suggested profiles, please restart!")
        ### REFRESH AKA REDO IT HERE!!
        return
    except NoSuchElementException:
        pass

    f_nr = 1
    for i in followers:
        if i.get_attribute("href"):
            users.add(i.get_attribute("href").split("/")[3])

            print(f"{f_nr})",  i.get_attribute("href").split("/")[3])
            f_nr += 1
        else:
            continue

        # time.sleep(.2) # could be removed

    current_followers = sorted(list(users))

    compare_followers(current_followers, username)


def compare_followers(current_followers, username):
    # If no file found create one for the user
    if not os.path.exists(f"{username}_follower.txt"):
        with open(f"{username}_follower.txt", "w") as file:
            file.write("\n".join(current_followers))
    # else compare them
    else:
        previous_followers = []     
        
        with open(f"{username}_follower.txt", "r") as file:
            previous_followers = [line.strip() for line in file]

        # Compare both lists (current_followers & previous_followers)
        new_abo = ",".join([entry for entry in current_followers if entry not in previous_followers]) # save new followers here
        lost_abo = ",".join([entry for entry in previous_followers if entry not in current_followers]) # save who unfollowed here
        
        # When new follower and someone unfollowed
        if new_abo and lost_abo:
            tle = "LOST AND GAINED FOLLOWERS!"
            msg = f"**{username}** had some changes!\n\nNew followers:\n{new_abo}\n\nLost followers:\n{lost_abo}"
            clr = 16577024

            # Overwrite follower list file with up-to-date list
            with open(f"{username}_follower.txt", "w") as file:
                file.write("\n".join(current_followers))

            send_notification(tle, msg, clr)
        # When new follower
        elif new_abo:
            tle = "NEW FOLLOWER!"
            msg = f"**{username}** got a new follower!\n\n{new_abo}"
            clr = 3407616

            # Overwrite follower list file with up-to-date list
            with open(f"{username}_follower.txt", "w") as file:
                file.write("\n".join(current_followers))

            send_notification(tle, msg, clr)
        # When someone unfollowed
        elif lost_abo:
            tle = "SOMEONE UNFOLLOWED!"
            msg = f"{username} lost a follower!\n\n{lost_abo}"
            clr = 16711680

            # Overwrite follower list file with up-to-date list
            with open(f"{username}_follower.txt", "w") as file:
                file.write("\n".join(current_followers))

            send_notification(tle, msg, clr)


def scrape_following(driver, username):
    # Open user profile
    driver.get(f"https://www.instagram.com/{username}/")
    time.sleep(3.5)
    
    # Open following
    WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/following')]"))).click()
    time.sleep(3)

    # Scroll through all following
    scroll_box = driver.find_element(By.XPATH, "//div[@class='_aano']")
    time.sleep(1)
    last_ht, ht = 0, 1  # height variables
    while last_ht != ht:
        last_ht = ht
        time.sleep(2)
        ht = driver.execute_script("""
                arguments[0].scrollTo(0, arguments[0].scrollHeight);
                return arguments[0].scrollHeight; """, scroll_box)

    # Start scraping following
    print(f"\n[Info] Scraping following for {username}...")

    users = set()

    following = driver.find_elements(By.XPATH, "//div[@class='_aano']//div[@class='x9f619 xjbqb8w x78zum5 x168nmei x13lgxp2 x5pf9jr xo71vjh x1uhb9sk x1plvlek xryxfnj x1c4vz4f x2lah0s x1q0g3np xqjyukv x1qjc9v5 x1oa3qoh x1nhvcw1']//a[contains(@href, '/')]")

    # do this to prevent suggested profiles at the end of the follower list
    try:
        driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[3]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[2]/div[2]/span")
        print("[WARN] Found suggested profiles, please restart!")
        ### REFRESH AKA REDO IT HERE!!
        return
    except NoSuchElementException:
        pass

    f_nr = 1
    for i in following:
        if i.get_attribute("href"):
            users.add(i.get_attribute("href").split("/")[3])

            print(f"{f_nr})" , i.get_attribute("href").split("/")[3])
            f_nr += 1
        else:
            continue

        # time.sleep(.2) # could be removed

    current_following = sorted(list(users))

    compare_following(current_following, username)


def compare_following(current_following, username):
    # If no file found create one for the user
    if not os.path.exists(f"{username}_following.txt"):
        with open(f"{username}_following.txt", "w") as file:
            file.write("\n".join(current_following))
    # else compare them
    else:
        previous_following = []     
        
        with open(f"{username}_following.txt", "r") as file:
            previous_following = [line.strip() for line in file]

        # Compare both lists (current_following & previous_following)
        new_abo = ",".join([entry for entry in current_following if entry not in previous_following]) # save new followers here
        lost_abo = ",".join([entry for entry in previous_following if entry not in current_following]) # save who unfollowed here
        
        # When new follower and someone unfollowed
        if new_abo and lost_abo:
            tle = "UNFOLLOWED AND FOLLOWED SOMEONE!"
            msg = f"**{username}** had some changes!\n\nNew following:\n{new_abo}\n\nUnfollowed:\n{lost_abo}"
            clr = 16577024

            # Overwrite following list file with up-to-date list
            with open(f"{username}_following.txt", "w") as file:
                file.write("\n".join(current_following))

            send_notification(tle, msg, clr)
        # When new following
        elif new_abo:
            tle = "NEW FOLLOWING!"
            msg = f"**{username}** started following someone!\n\n{new_abo}"
            clr = 3407616

            # Overwrite following list file with up-to-date list
            with open(f"{username}_following.txt", "w") as file:
                file.write("\n".join(current_following))

            send_notification(tle, msg, clr)
        # When someone was unfollowed
        elif lost_abo:
            tle = "SOMEONE WAS UNFOLLOWED!"
            msg = f"{username} unfollowed someone!\n\n{lost_abo}"
            clr = 16711680

            # Overwrite following list file with up-to-date list
            with open(f"{username}_following.txt", "w") as file:
                file.write("\n".join(current_directory))

            send_notification(tle, msg, clr)


def send_notification(title, message, color):
    discord_webhook = "CHANGEME"

    payload = {
        "username": "Instagram Scraper",
        "avatar_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Instagram_logo_2016.svg/2048px-Instagram_logo_2016.svg.png",
        "embeds": [
            {
                "title": title,
                "description": message,
                "color": color
            }
        ]
    }
    headers = {"Content-Type": "application/json"}

    # Send POST request to Webhook
    response = requests.post(discord_webhook, json=payload, headers=headers)

    if response.status_code == 204:
        print("[INFO] Notification sent successfully.")
    else:
        print("[WARN] Failed to send notification!")


### -----------------------------------------------------------------------------------
### -----------------------------------------------------------------------------------
### -----------------------------------------------------------------------------------

# Welcome ASCII art
tprint("Insta - Scraper")
print("\x1B[3mby casudo\x1B[0m")
print(f"\x1B[3m{VERSION}\x1B[0m\n\n")

# Get login information
credentials = load_credentials()
if credentials is None:
    print("[WARN] No credentials found, please enter them:\n")
    username, password = prompt_credentials()
else:
    print("[INFO] Loaded credentials from file.")
    username, password = credentials

# Set options for browser
options = Options()
options.add_experimental_option("detach", True)
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--log-level=3")
current_directory = os.getcwd()
options.add_argument(f"--user-data-dir={current_directory}/{username}_profile")
# Mobile version
mobile_emulation = {
        "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/90.0.1025.166 Mobile Safari/535.19"}
options.add_experimental_option("mobileEmulation", mobile_emulation)

# Start browser
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Login (start the program)
login(driver, username, password)

# End session
print("\n[INFO] All done, quitting.")
driver.quit()