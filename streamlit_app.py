import streamlit as st
import os
import time
import platform
import tempfile
import subprocess
from PIL import Image
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

def is_mac():
    return platform.system() == 'Darwin'

def copy_image_to_clipboard(img_path):
    """Copy image to clipboard based on platform."""
    st.write(f"DEBUG: Attempting to copy image to clipboard: {img_path}")
    try:
        if is_mac():
            applescript = f'''
            set theFile to POSIX file "{img_path}"
            set theImage to (read theFile as JPEG picture)
            set the clipboard to theImage
            '''
            subprocess.run(['osascript', '-e', applescript])
        else:
            subprocess.run(['xclip', '-selection', 'clipboard', '-t', 'image/png', '-i', img_path])
        st.write("DEBUG: Image copied to clipboard successfully")
    except Exception as e:
        st.write(f"DEBUG: Clipboard operation failed but continuing: {str(e)}")

@st.cache_resource
def get_driver():
    """Initialize and cache the webdriver."""
    import undetected_chromedriver as uc
    
    try:
        options = uc.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--window-size=1920,1080")
        
        driver = uc.Chrome(options=options)
        return driver
    except Exception as e:
        st.error(f"Failed to initialize webdriver: {str(e)}")
        raise

class VizcomAutomation:
    def __init__(self, driver, wait_time=30):
        self.driver = driver
        self.wait = WebDriverWait(driver, wait_time)
        
    def login(self, username, password):
        """Handle login process."""
        self.driver.get("https://app.vizcom.ai/files/team/2f8f9d59-a5b8-4175-b258-e339144008a5")
        
        # Email
        email_input = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='email']")))
        email_input.send_keys(username)
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.jRuTWx"))).click()
        
        # Password
        time.sleep(2)
        password_input = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='password']")))
        password_input.send_keys(password)
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.jRuTWx"))).click()

    def setup_new_project(self):
        """Navigate to new project and set it up."""
        time.sleep(2)
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'New file')]"))).click()
        time.sleep(2)
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Start in Studio']"))).click()
        time.sleep(3)
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Landscape']"))).click()
        time.sleep(2)
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//button[text()='Create']"))).click()

    def paste_model_image(self):
        """Paste the model image into the canvas."""
        time.sleep(2)
        canvas = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.cQHQvu")))
        self.driver.execute_script("arguments[0].click();", canvas)
        actions = ActionChains(self.driver)
        actions.key_down(Keys.COMMAND).send_keys('v').key_up(Keys.COMMAND).perform()
        time.sleep(2)

    def apply_style_settings(self, style_image_path, style_strength):
        """Apply style settings including uploading style image."""
        # Add style
        add_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.gEjJrb")))
        self.driver.execute_script("arguments[0].click();", add_button)
        
        # Click style button
        time.sleep(2)
        style_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Style']")))
        self.driver.execute_script("arguments[0].click();", style_button)
        
        # Upload style image
        time.sleep(2)
        upload_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Upload...']")))
        self.driver.execute_script("arguments[0].click();", upload_button)
        file_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='file']")
        file_input.send_keys(style_image_path)
        
        # Set strength
        time.sleep(2)
        percentage_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.sc-dBfUQs.gOSsgq")))
        percentage_button.click()
        percentage_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input.sc-kLgxMn.eVooDm")))
        percentage_input.send_keys(style_strength)

    def generate_image(self, prompt):
        """Generate image with given prompt and wait for completion."""
        prompt_textarea = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "textarea.fmJnQo")))
        prompt_textarea.clear()
        prompt_textarea.send_keys(prompt)
        
        time.sleep(2)
        generate_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.sc-gJFNMl.kLShra")))
        self.driver.execute_script("arguments[0].click();", generate_button)
        
        # Wait for generation
        start_time = time.time()
        while time.time() - start_time < 120:  # 2 minute timeout
            try:
                add_button = self.driver.find_element(By.CSS_SELECTOR, "button.sc-gJFNMl.kJmtTh")
                button_html = add_button.get_attribute('outerHTML')
                st.write(f"DEBUG: Button HTML: {button_html}")
                if "disabled" not in button_html:
                    st.write("DEBUG: Generation complete")
                    return True
            except Exception as e:
                st.write(f"DEBUG: Waiting for generation... {str(e)}")
            time.sleep(5)
        return False

def process_screenshot(screenshot_path):
    """Process and crop the screenshot."""
    with Image.open(screenshot_path) as img:
        width, height = img.size
        left = width // 4
        top = height // 4
        right = width * 3 // 4
        bottom = height * 3 // 4
        cropped = img.crop((left, top, right, bottom))
        cropped_path = os.path.join(os.path.dirname(screenshot_path), "cropped_result.png")
        cropped.save(cropped_path)
        return cropped_path

def run_automation(model_image_path, styling_image_path, rendering_prompt, 
                  styling_strength, vizcom_username, vizcom_password, progress_bar):
    """Main automation function."""
    try:
        driver = get_driver()
        automation = VizcomAutomation(driver)
        
        # Execute steps
        progress_bar.progress(10)
        copy_image_to_clipboard(model_image_path)
        
        progress_bar.progress(20)
        automation.login(vizcom_username, vizcom_password)
        
        progress_bar.progress(40)
        automation.setup_new_project()
        
        progress_bar.progress(60)
        automation.paste_model_image()
        
        progress_bar.progress(70)
        automation.apply_style_settings(styling_image_path, styling_strength)
        
        progress_bar.progress(80)
        if automation.generate_image(rendering_prompt):
            progress_bar.progress(90)
            
            # Take and process screenshot
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_screenshot:
                driver.save_screenshot(tmp_screenshot.name)
                cropped_path = process_screenshot(tmp_screenshot.name)
                with open(cropped_path, 'rb') as f:
                    screenshot_bytes = f.read()
                progress_bar.progress(100)
                return screenshot_bytes
        else:
            st.error("Generation timed out")
            return None
            
    except Exception as e:
        st.error(f"Automation error: {str(e)}")
        if driver:
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_error:
                driver.save_screenshot(tmp_error.name)
                with open(tmp_error.name, 'rb') as f:
                    return f.read()
        return None

def main():
    st.title("Vizcom Automation Tool")

    with st.expander("Environment Information"):
        st.write(f"Running on: {platform.system()}")
        st.write(f"Platform: {platform.platform()}")

    # File uploads and inputs
    model_image = st.file_uploader("Upload Model Image", type=['png', 'jpg', 'jpeg'])
    styling_image = st.file_uploader("Upload Styling Image", type=['png', 'jpg', 'jpeg'])

    col1, col2 = st.columns(2)
    with col1:
        rendering_prompt = st.text_input("Rendering Prompt")
        styling_strength = st.text_input("Styling Strength (0-100)", "85")
    with col2:
        vizcom_username = st.text_input("Vizcom Username")
        vizcom_password = st.text_input("Vizcom Password", type="password")

    if st.button("Run Automation") and model_image and styling_image:
        # Save temporary files
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_model:
            tmp_model.write(model_image.getvalue())
            model_path = tmp_model.name

        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_style:
            tmp_style.write(styling_image.getvalue())
            style_path = tmp_style.name

        try:
            progress_bar = st.progress(0)
            st.write("Starting automation process...")

            result = run_automation(
                model_path,
                style_path,
                rendering_prompt,
                styling_strength,
                vizcom_username,
                vizcom_password,
                progress_bar
            )

            if result:
                st.write("Automation completed!")
                st.image(result, caption="Final Result", use_column_width=True)
                st.download_button(
                    label="Download Result",
                    data=result,
                    file_name="vizcom_result.png",
                    mime="image/png"
                )
            else:
                st.error("Failed to generate result")

        except Exception as e:
            st.error(f"Process failed: {str(e)}")
        finally:
            os.unlink(model_path)
            os.unlink(style_path)

if __name__ == "__main__":
    main()
