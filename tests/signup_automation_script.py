"""
Signup Automation Script - Step 1: Personal Details
Site: https://authorized-partner.vercel.app/
Framework: Selenium + Python + pytest
Author: QA Intern Task
"""

import pytest
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


# CONFIGURATION

# Base_url
BASE_URL = "https://authorized-partner.vercel.app/"

# Test Data
TEST_USER = {
    "first_name" : "",
    "last_name" : "",
    "email" : "",
    "phone": "",
    "password" : "",
    "confirm_password" : "",
}

# Driver Setup

@pytest.fixture(scope="module")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicity_wait(5)
    yield driver
    driver.quit()
