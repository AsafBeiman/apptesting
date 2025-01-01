import streamlit as st
import os
import time
import tempfile
from PIL import Image
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
from pyvirtualdisplay import Display


@st.cache_resource
def get_driver():
    # Initialize virtual display
    display = Display(visible=0, size=(1920, 1080))
    display.start()

    # Initialize Firefox options
    options = Options()
    options.set_preference("general.useragent.override",
                           "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0")
    options.set_preference("dom.webdriver.enabled", False)
    options.set_preference("useAutomationExtension", False)

    # Set up Firefox WebDriver
    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=options)
    driver.set_window_size(1920, 1080)

    return driver, display

def run_automation(model_image_path, styling_image_path, rendering_prompt,
                   styling_strength, vizcom_username, vizcom_password, progress_bar):
    driver, display = get_driver()
    wait = WebDriverWait(driver, 60)  # Increased timeout to 60 seconds

    try:
        # Navigate to the website
        # st.write("Navigating to website...")
        driver.get("https://app.vizcom.ai/auth")
        progress_bar.progress(10)
        time.sleep(3)  # Increased initial wait time


        # Login process
        # st.write("Logging in...")
        email_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")))
        email_input.clear()
        email_input.send_keys(vizcom_username)
        progress_bar.progress(20)

        login_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.jRuTWx")))
        driver.execute_script("arguments[0].click();", login_button)
        time.sleep(3)

        progress_bar.progress(30)
        password_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']")))
        password_input.clear()
        password_input.send_keys(vizcom_password)

        submit_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.jRuTWx")))
        driver.execute_script("arguments[0].click();", submit_button)
        time.sleep(3)
        progress_bar.progress(40)
        time.sleep(3)

        # st.write("Navigating to studio...")
        new_file_link = wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'New file')]")))
        driver.execute_script("arguments[0].click();", new_file_link)
        time.sleep(3)
        start_studio = wait.until(EC.presence_of_element_located((By.XPATH, "//span[text()='Start in Studio']")))
        driver.execute_script("arguments[0].click();", start_studio)
        time.sleep(3)

        landscape = wait.until(EC.presence_of_element_located((By.XPATH, "//span[text()='Landscape']")))
        driver.execute_script("arguments[0].click();", landscape)
        time.sleep(3)

        progress_bar.progress(50)
        upload_image_button = wait.until(
            EC.presence_of_element_located((By.XPATH, "//button[text()='Upload an image']")))
        driver.execute_script("arguments[0].click();", upload_image_button)

        image_file_input = driver.find_element(By.CSS_SELECTOR, "input[type='file']")
        image_file_input.send_keys(model_image_path)
        time.sleep(3)

        progress_bar.progress(60)
        add_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.gEjJrb")))
        driver.execute_script("arguments[0].click();", add_button)
        time.sleep(3)

        style_button = wait.until(EC.presence_of_element_located((By.XPATH, "//button[text()='Style']")))
        driver.execute_script("arguments[0].click();", style_button)
        time.sleep(3)

        upload_button = wait.until(EC.presence_of_element_located((By.XPATH, "//button[text()='Upload...']")))
        driver.execute_script("arguments[0].click();", upload_button)

        file_input = driver.find_element(By.CSS_SELECTOR, "input[type='file']")
        file_input.send_keys(styling_image_path)
        time.sleep(3)


        progress_bar.progress(70)
        percentage_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.sc-dBfUQs.gOSsgq")))
        percentage_button.click()
        time.sleep(0.5)
        percentage_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input.sc-kLgxMn.eVooDm")))
        percentage_input.send_keys(str(styling_strength))
        time.sleep(3)

        progress_bar.progress(75)
        prompt_textarea = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "textarea.fmJnQo")))
        prompt_textarea.clear()
        prompt_textarea.send_keys(rendering_prompt)
        progress_bar.progress(80)
        time.sleep(3)

        generate_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.sc-gJFNMl.kLShra")))
        driver.execute_script("arguments[0].click();", generate_button)
        progress_bar.progress(90)

        # Wait for generation to complete
        start_time = time.time()
        while time.time() - start_time < 120:  # 2 minute timeout
            add_button = driver.find_element(By.CSS_SELECTOR, "button.sc-gJFNMl.kJmtTh")
            button_html = add_button.get_attribute('outerHTML')
            if "disabled" not in button_html:
                # st.write("Generation complete")
                break
            time.sleep(5)

        time.sleep(3)  # Additional wait for final render
        img = driver.get_screenshot_as_png()
        progress_bar.progress(100)
        return img

    except Exception as e:
        st.error(f"Automation error: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return None
    finally:
        driver.quit()
        display.stop()
