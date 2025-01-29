import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# Load environment variables
load_dotenv()

MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
PO_NUMBER = 'P019558'
# PO_NUMBER = os.getenv("PO_NUMBER")

# Check if credentials are set
if not MAIL_USERNAME or not MAIL_PASSWORD:
    print("Email credentials not found in .env file.")
    exit()

# Set up Selenium WebDriver
chrome_options = Options()
chrome_options.add_argument("--start-maximized")  # Start the browser maximized
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--disable-extensions")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

try:
    # Open the webmail login page
    driver.get("https://mail.cafoy.com:2096/login/?user=s2foy@cafoy.com")

    # Locate and fill the password field
    password_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "pass"))
    )
    password_field.send_keys(MAIL_PASSWORD)

    # Submit the login form
    password_field.send_keys(Keys.RETURN)

    # Wait for the search box to be present
    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "_q"))
    )

    # Enter the PO number into the search box
    search_box.click()  # Ensure the search box is focused
    search_box.send_keys(PO_NUMBER)
    time.sleep(3)
    search_box.send_keys(Keys.RETURN)

    print(f"Search for PO number '{PO_NUMBER}' completed successfully.")

      # Wait for the search results to load
    first_email_link = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "(//tr[@class='message thread unroot']//a)[1]"))
)
    actions = ActionChains(driver)
    actions.double_click(first_email_link).perform()


    # Click on the first email
    print("Clicked on the first email in the search results.")
      # Wait for the attachments list to be present
    
    attachment_list = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "attachmentslist"))
    )

    # Locate all attachment items
    attachments = attachment_list.find_elements(By.TAG_NAME, "li")

 # Iterate through attachments to find the PDF file
    for attachment in attachments:
        attachment_name = attachment.find_element(By.CLASS_NAME, "attachment-name").text
        if attachment_name.endswith(".pdf"):
            print(f"Found PDF attachment: {attachment_name}")
            # Locate the options menu next to the PDF file
            options_menu = attachment.find_element(By.CLASS_NAME, "drop.skip-content")
            options_menu.click()  # Click the options menu
            print("Clicked on the options menu for the PDF attachment.")

            
            # Ensure menu is visible and download button is interactable
            options_menu = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "attachmentmenu"))
            )

            # Attempt to locate the download button
            try:
            # Locate the second <li> item in the options menu (Download button)
                menu_items = options_menu.find_elements(By.TAG_NAME, "li")

                if len(menu_items) > 1:
                    download_button = menu_items[1].find_element(By.TAG_NAME, "a")
                    download_button.click()
            except Exception as e:
                print(f"Failed to click using Selenium. Attempting JavaScript click. Error: {e}")
                # Use JavaScript as a fallback to click the button
                driver.execute_script("arguments[0].click();", options_menu.find_element(By.ID, "attachmenuDownload"))
                print("Download button clicked using JavaScript.")
            break
    else:
        print("No PDF attachment found.")
    
except Exception as e:
    print(f"An error occurred: {e}")

finally:
    print("Script execution complete. The browser will remain open for 300 seconds.")
    time.sleep(300)  # Keeps the browser open for 5 minutes before quitting
    driver.quit()

