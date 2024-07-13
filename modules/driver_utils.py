import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from modules.config import Config
import time
import psutil

class DriverUtils:
    @staticmethod
    def close_existing_chrome_instances():
        """
        Close existing Chrome instances by terminating their processes.
        """
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == 'chrome' or proc.info['name'] == 'chrome.exe':
                proc.terminate()
                try:
                    proc.wait(timeout=3)
                except psutil.TimeoutExpired:
                    proc.kill()
    
    @staticmethod
    def create_driver():
        """
        Create and return a Chrome WebDriver instance.

        Returns:
        - webdriver.Chrome: Initialized Chrome WebDriver instance.
        """
        driver_path = "chromedriver/chromedriver.exe"  # Adjust path as necessary
        service = Service(driver_path)  # Create a WebDriver service
        
        # Initialize Chrome WebDriver with service and options
        driver = webdriver.Chrome(service=service, options=Config.get_chrome_options())
        driver.maximize_window()  # Maximize the window
        
        return driver  # Return the initialized WebDriver instance
    
    @staticmethod
    def quit_driver(driver):
        try:
            print(f"Quitting driver...")
            driver.quit()
                
        except Exception as e:
            print(f"Error quitting driver  {e}")
    


    @staticmethod
    def access_site(driver, url):
        """
        Access the subreddit page using the provided WebDriver instance.

        Args:
        - driver (webdriver.Chrome): Chrome WebDriver instance.
        """
        driver.get(url) 
        time.sleep(3)

    @staticmethod
    def get_document_element(driver):
        """
        Retrieve the HTML content of the entire document using the provided WebDriver instance.

        Args:
        - driver (webdriver.Chrome): Chrome WebDriver instance.

        Returns:
        - str: Outer HTML content of the document.
        """
        return driver.execute_script("return document.documentElement.outerHTML;")  # Execute JavaScript to return outer HTML content

