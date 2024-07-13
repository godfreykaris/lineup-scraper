import os
import time
import pandas as pd

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from modules.driver_utils import DriverUtils
from modules.retrieve_names import ImageProcessor
import modules.shared as shared

# Function to ensure the directory exists
def ensure_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# URL of the website to scrape
url = "https://www.fantasyfootballhub.co.uk/premier-league-predicted-lineups"  # Replace with your actual URL

# Path to the downloads folder
downloads_folder = "downloads"

# Ensure the downloads folder exists
ensure_directory(downloads_folder)

# Configure Chrome options to automatically download files to the downloads folder
chrome_options = webdriver.ChromeOptions()
prefs = {"download.default_directory": os.path.abspath(downloads_folder)}
chrome_options.add_experimental_option("prefs", prefs)

DriverUtils.close_existing_chrome_instances()

# Start the Chrome browser
driver = DriverUtils.create_driver()

tesseract_location = shared.tesseract_location
image_processor = ImageProcessor(tesseract_location)

try:
    # Navigate to the URL
    driver.get(url)
    time.sleep(10)  # Add a delay to allow content to load (adjust as necessary)

    # Find and close the modal if present
    try:
        div_element = driver.find_element(By.CSS_SELECTOR, '[data-cy="close-modal-button"]')
        div_element.click()
    except Exception as e:
        print("No modal to close.")

    time.sleep(5)

    # Find and reject cookies if the button is present
    try:
        button_element = driver.find_element(By.XPATH, '//button[@class="cky-btn cky-btn-reject" and @aria-label="Reject All"]')
        button_element.click()
    except Exception as e:
        print("No cookies to reject.")

    # Get the initial viewport height
    viewport_height = driver.execute_script("return window.innerHeight;")
    
    # Set the scroll amount (adjust as necessary, e.g., scroll by half of the viewport height)
    scroll_amount = viewport_height // 2
    
    # Initial scroll position
    scroll_position = 0

    # Get initial height of the webpage
    last_height = driver.execute_script("return document.body.scrollHeight")

    downloaded_images = []
    team_players = []
    teams = []
    teams_count = 0

    # Find all <h2> elements
    h2_elements = driver.find_elements(By.TAG_NAME, 'h2')
    for h2 in h2_elements:
        strong_tags = h2.find_elements(By.TAG_NAME, 'strong')
        if len(strong_tags) == 2:
            team_name = strong_tags[0].text.strip() + strong_tags[1].text.strip().split(' ')[0]
            team_name = team_name.replace('predicted', '').strip()
            teams.append(team_name)
            print(f"Team: {team_name}")

    while True:
        # Scroll down to bottom of the page
        driver.execute_script(f"window.scrollBy(0, {scroll_amount});")

        # Find the image element inside the div that follows the <h2> element
        try:
            image_elements = driver.find_elements(By.TAG_NAME, 'img')
            # Iterate through each image element and download the image if it matches the desired pattern
            for idx, image_element in enumerate(image_elements):
                image_url = image_element.get_attribute('srcset').split(' ')[0]

                if '_next/image' in image_url:
                    if not image_url.startswith('https'):
                        absolute_image_url = "https://www.fantasyfootballhub.co.uk" + image_url
                    else:
                        continue

                    if image_url in downloaded_images:
                        continue

                    downloaded_images.append(image_url)

                    # Construct the filename based on the team name
                    image_name = f"{teams[teams_count]}.avif"  # Adjust file extension based on actual image format

                    # Download the image using requests
                    response = requests.get(absolute_image_url)

                    # Save the image to the downloads folder
                    image_path = os.path.join(downloads_folder, image_name)
                    with open(image_path, 'wb') as f:
                        f.write(response.content)

                    players = image_processor.process_image_and_extract_names(image_path, teams[teams_count])
                    print(players)
                    team_players.append(players)

                    teams_count += 1

        except Exception as e:
            print(f"No image found.")
            break

        # Check if new images are loaded
        new_height = last_height + scroll_amount
        if new_height == last_height:
            break
        last_height = new_height

    teams_players = pd.concat(team_players, axis=1)

    print(teams_players)

    print("All images downloaded successfully!")

finally:
    DriverUtils.quit_driver(driver)
