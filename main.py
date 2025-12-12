import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import os
import io

# --- Helper Functions for Selenium and Cookies ---

# Use st.cache_resource to ensure the driver instance is reused across Streamlit reruns
@st.cache_resource
def initialize_driver():
    """Initializes and returns a Chrome WebDriver."""
    st.info("Initializing Chrome Driver...")
    try:
        # Chrome Options for better control
        chrome_options = webdriver.ChromeOptions()
        # You can add options like headless mode, or a specific user profile
        # chrome_options.add_argument("--headless") # Uncomment for headless mode (no visible browser)
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        # To make the browser stay open after script finishes (useful for debugging)
        chrome_options.add_experimental_option("detach", True)
        # Optionally, use a persistent user profile (alternative to cookies for login)
        # profile_dir = os.path.abspath("chrome_profile")
        # os.makedirs(profile_dir, exist_ok=True)
        # chrome_options.add_argument(f"user-data-dir={profile_dir}")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        st.success("Chrome Driver initialized.")
        return driver
    except Exception as e:
        st.error(f"Error initializing Chrome Driver: {e}")
        st.error("Please ensure Chrome is installed and updated.")
        return None

def load_cookies(driver, cookie_path, url):
    """Loads cookies from a file into the driver."""
    if os.path.exists(cookie_path):
        try:
            with open(cookie_path, 'r') as f:
                cookies = json.load(f)
            driver.get(url)  # Must navigate to the domain before adding cookies
            for cookie in cookies:
                # Selenium expects 'expiry' to be an integer timestamp
                if 'expiry' in cookie:
                    cookie['expiry'] = int(cookie['expiry'])
                driver.add_cookie(cookie)
            driver.refresh() # Refresh the page to apply cookies
            st.success(f"Cookies loaded from {cookie_path}. Refreshing page...")
            time.sleep(3) # Give some time for cookies to apply and page to load
            return True
        except Exception as e:
            st.error(f"Failed to load cookies: {e}")
            return False
    else:
        st.warning(f"No cookie file found at '{cookie_path}'. You will need to log in manually.")
        return False

def save_cookies(driver, cookie_path):
    """Saves current browser cookies to a file."""
    try:
        with open(cookie_path, 'w') as f:
            json.dump(driver.get_cookies(), f, indent=4)
        st.success(f"Cookies saved to {cookie_path}")
        return True
    except Exception as e:
        st.error(f"Failed to save cookies: {e}")
        return False

def close_driver(driver):
    """Closes the browser driver."""
    if driver:
        driver.quit()
        st.success("Browser closed.")
        # Clear the cached resource
        initialize_driver.clear()
        return True
    return False

# --- PLATFORM-SPECIFIC MESSAGE SENDING FUNCTION (CUSTOMIZE THIS!) ---
def send_single_message(driver, recipient_identifier, message_text, send_delay_seconds):
    """
    Automates sending a single message to a recipient on the chosen messenger platform.
    YOU MUST CUSTOMIZE THIS FUNCTION FOR YOUR SPECIFIC MESSENGER (e.g., WhatsApp Web, FB Messenger).
    """
    try:
        st.info(f"Attempting to send to: '{recipient_identifier}'...")

        # --- EXAMPLE FOR A HYPOTHETICAL MESSENGER PLATFORM ---
        # Replace these with actual XPATHs or CSS Selectors from your chosen platform

        # 1. Search for the recipient or navigate to their chat
        # This part is highly dependent on the messenger's UI.
        # It might involve searching in a search bar, clicking a contact, or navigating directly via URL if possible.
        # For simplicity, we'll assume the chat is already open or can be opened easily.

        # Example: Find a search box, type the recipient, and press Enter
        # search_box_xpath = "//div[@contenteditable='true'][@data-tab='3']" # Example for WhatsApp search
        # search_box = WebDriverWait(driver, 20).until(
        #     EC.presence_of_element_located((By.XPATH, search_box_xpath))
        # )
        # search_box.clear()
        # search_box.send_keys(recipient_identifier)
        # time.sleep(2) # Wait for search results to appear
        # search_box.send_keys(Keys.ENTER) # Select the first result (usually)
        # time.sleep(5) # Wait for the chat to load

        # For demonstration, we'll just log and simulate.
        # In a real scenario, you'd navigate to the chat for 'recipient_identifier'.
        # For example, for WhatsApp, after logging in:
        # driver.get(f"https://web.whatsapp.com/send?phone={recipient_identifier}") # If recipient_identifier is a phone number
        # time.sleep(5) # Wait for chat to load

        # You might need to click on the contact in the left panel
        # recipient_element_xpath = f"//span[@title='{recipient_identifier}']" # Example by name
        # WebDriverWait(driver, 10).until(
        #     EC.element_to_be_clickable((By.XPATH, recipient_element_xpath))
        # ).click()
        # time.sleep(3)


        # 2. Locate the message input field
        # message_input_xpath = "//div[@contenteditable='true'][@data-tab='1']" # Example for WhatsApp message input
        # message_input_field = WebDriverWait(driver, 20).until(
        #     EC.presence_of_element_located((By.XPATH, message_input_xpath))
        # )
        # message_input_field.send_keys(message_text)

        # 3. Locate and click the send button
        # send_button_xpath = "//button[@data-testid='send']" # Example for WhatsApp send button
        # send_button = WebDriverWait(driver, 10).until(
        #     EC.element_to_be_clickable((By.XPATH, send_button_xpath))
        # )
        # send_button.click()

        # --- SIMULATION (REMOVE THIS AND UNCOMMENT REAL CODE ABOVE) ---
        st.warning(f"SIMULATING: Sending message to '{recipient_identifier}' with content: '{message_text[:100]}...'")
        time.sleep(send_delay_seconds) # Simulate the time it takes to send
        # --- END SIMULATION ---

        st.success(f"Message sent (or simulated) to '{recipient_identifier}'!")
        return True
    except Exception as e:
        st.error(f"Failed to send message to '{recipient_identifier}': {e}")
        st.exception(e) # Display full traceback for debugging
        return False

# --- Streamlit UI ---

st.set_page_config(layout="wide", page_title="Local Messenger Automation Tool")
st.title("🚀 Local Messenger Automation Tool")
st.markdown("---")

st.sidebar.header("Configuration")
messenger_url = st.sidebar.text_input("Messenger Web URL", "https://web.whatsapp.com", help="e.g., https://web.whatsapp.com or https://www.messenger.com")
cookie_file_path = st.sidebar.text_input("Cookie File Name", "cookies.json", help="Path to save/load browser cookies for login persistence.")
message_delay_seconds = st.sidebar.slider("Message Send Delay (seconds)", 0.5, 15.0, 3.0, help="Time to wait between sending messages to different recipients.")

st.sidebar.markdown("---")
st.sidebar.header("Browser Control")

driver_instance = None
if 'driver' not in st.session_state:
    st.session_state.driver = None

if st.sidebar.button("Initialize & Open Browser"):
    st.session_state.driver = initialize_driver()
    if st.session_state.driver:
        st.session_state.driver.get(messenger_url)
        if load_cookies(st.session_state.driver, cookie_file_path, messenger_url):
            st.info("Cookies loaded. Check the browser window to confirm login.")
        else:
            st.warning("Please log in manually in the opened browser window.")
        st.info("Browser opened. You have ~30 seconds to log in manually if needed.")
        time.sleep(30) # Grace period for manual login or QR scan
        st.sidebar.success("Browser is ready.")
elif st.session_state.driver:
    st.sidebar.success("Browser is already open and initialized.")


if st.sidebar.button("Save Current Cookies"):
    if st.session_state.driver:
        save_cookies(st.session_state.driver, cookie_file_path)
    else:
        st.sidebar.warning("Browser not initialized. Please open it first.")

if st.sidebar.button("Close Browser"):
    if st.session_state.driver:
        close_driver(st.session_state.driver)
        st.session_state.driver = None
    else:
        st.sidebar.info("No browser is currently open.")

st.markdown("---")

st.header("Recipient Information")
recipient_mode = st.radio("How to specify recipients?", ["Single Recipient", "Upload Recipient File"], horizontal=True)

recipients = []
if recipient_mode == "Single Recipient":
    single_recipient_id = st.text_input("Enter Single Recipient UID/Name", help="e.g., 'John Doe' or a phone number for WhatsApp")
    if single_recipient_id:
        recipients.append(single_recipient_id)
else:
    recipient_file = st.file_uploader("Upload Recipient List (one UID/Name per line)", type=["txt"])
    if recipient_file:
        string_data = io.StringIO(recipient_file.getvalue().decode("utf-8")).read()
        recipients = [line.strip() for line in string_data.splitlines() if line.strip()]
        st.info(f"Loaded {len(recipients)} recipients.")

st.header("Messages to Send")
message_source = st.radio("How to specify messages?", ["Single Message", "Upload Message File"], horizontal=True)

messages = []
if message_source == "Single Message":
    single_message_text = st.text_area("Enter Single Message")
    if single_message_text:
        messages.append(single_message_text)
else:
    message_file = st.file_uploader("Upload Message List (one message per line)", type=["txt"])
    if message_file:
        string_data = io.StringIO(message_file.getvalue().decode("utf-8")).read()
        messages = [line.strip() for line in string_data.splitlines() if line.strip()]
        st.info(f"Loaded {len(messages)} messages.")

st.markdown("---")

if st.button("🔴 Start Sending Messages", type="primary"):
    if not st.session_state.driver:
        st.error("Please initialize and open the browser first.")
    elif not recipients:
        st.error("Please specify at least one recipient.")
    elif not messages:
        st.error("Please specify at least one message to send.")
    else:
        st.subheader("Sending Process Log:")
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        total_recipients = len(recipients)
        for i, recipient in enumerate(recipients):
            message_to_send = messages[i % len(messages)] # Cycle through messages if fewer messages than recipients
            status_text.info(f"Processing recipient {i+1}/{total_recipients}: **{recipient}**")
            
            # Call the platform-specific message sending function
            send_single_message(st.session_state.driver, recipient, message_to_send, message_delay_seconds)
            
            progress_bar.progress((i + 1) / total_recipients)
            time.sleep(1) # Small pause for UI update

        st.success("✅ All messages processed! Don't forget to save cookies if your login session updated.")
        st.balloons()