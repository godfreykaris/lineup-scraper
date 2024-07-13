import os
import time
import requests
from urllib.parse import urlparse, urljoin
from selenium import webdriver
from selenium.webdriver.common.by import By
from modules.driver_utils import DriverUtils
import re

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

try:
    # Navigate to the URL
    driver.get(url)
    time.sleep(10)  # Add a delay to allow content to load (adjust as necessary)
    # Find the <div> element using its data-cy attribute
    div_element = driver.find_element(By.CSS_SELECTOR, '[data-cy="close-modal-button"]')

    # Click on the <div> element
    div_element.click()

    time.sleep(5)

     # Find the <button> element using its class name and aria-label
    button_element = driver.find_element(By.XPATH, '//button[@class="cky-btn cky-btn-reject" and @aria-label="Reject All"]')

    # Click on the <button> element
    button_element.click()

     # Get the initial viewport height
    viewport_height = driver.execute_script("return window.innerHeight;")
    
    # Set the scroll amount (adjust as necessary, e.g., scroll by half of the viewport height)
    scroll_amount = viewport_height // 2
    
    # Initial scroll position
    scroll_position = 0

    # Get initial height of the webpage
    last_height = driver.execute_script("return document.body.scrollHeight")

    downloaded_images = []

    while True:
        # Scroll down to bottom of the page
        driver.execute_script(f"window.scrollBy(0, {scroll_amount});")

        time.sleep(1)

        image_elements = driver.find_elements(By.TAG_NAME, 'img')

        # Iterate through each image element and download the image if it matches the desired pattern
        for idx, image_element in enumerate(image_elements):
            # Get the image src attribute
            image_url = image_element.get_attribute('srcset').split(' ')[0]

            # Check if image_url starts with 'https' and contains '_next/image'
            if  '_next/image' in image_url:
                if not image_url.startswith('https'):
                    absolute_image_url = "https://www.fantasyfootballhub.co.uk" + image_url
                else:
                    continue
                

                if len(downloaded_images) <= 2:
                    downloaded_images.append(image_url)
                    continue
                
                if image_url in downloaded_images:
                    continue
                
                else:
                    downloaded_images.append(image_url)
                    
                print(f"Downloading image from {absolute_image_url}")

                # Construct the filename based on index and image URL
                image_name = f"image_{idx}.avif"  # Adjust file extension based on actual image format

                # Download the image using requests
                response = requests.get(absolute_image_url)

                # Save the image to the downloads folder
                image_path = os.path.join(downloads_folder, image_name)
                with open(image_path, 'wb') as f:
                    f.write(response.content)

                print(f"Downloaded {image_name}")

        # Check if new images are loaded
        new_height = scroll_position + scroll_amount
        scroll_position = new_height
        if new_height == last_height:
            break

    

    print("All images downloaded successfully!")

finally:
    DriverUtils.quit_driver(driver)
