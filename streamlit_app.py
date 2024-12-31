# import streamlit as st
# import pyvista as pv
# import tempfile
# import os
# from datetime import datetime

# # Initialize PyVista
# pv.start_xvfb()
# st.set_page_config(layout="wide")

# # Preset views
# PRESET_VIEWS = {
#     'Front': {'azimuth': 0, 'elevation': 0},
#     'Right': {'azimuth': 90, 'elevation': 0},
#     'Left': {'azimuth': -90, 'elevation': 0},
#     'Back': {'azimuth': 180, 'elevation': 0},
#     'Top': {'azimuth': 0, 'elevation': 90},
#     'Top Right Front': {'azimuth': 45, 'elevation': 45},
#     'Top Right Back': {'azimuth': 135, 'elevation': 45},
#     'Top Left Front': {'azimuth': -45, 'elevation': 45},
#     'Top Left Back': {'azimuth': -135, 'elevation': 45},
#     'Bottom Right Front': {'azimuth': 45, 'elevation': -45},
#     'Bottom Right Back': {'azimuth': 135, 'elevation': -45},
#     'Bottom Left Front': {'azimuth': -45, 'elevation': -45},
#     'Bottom Left Back': {'azimuth': -135, 'elevation': -45},
# }

# # Initialize session state
# if 'plotter' not in st.session_state:
#     st.session_state.plotter = None
# if 'mesh_path' not in st.session_state:
#     st.session_state.mesh_path = None
# if 'captured_views' not in st.session_state:
#     st.session_state.captured_views = []
# if 'azimuth' not in st.session_state:
#     st.session_state.azimuth = 45  # Default Top Right Front
# if 'elevation' not in st.session_state:
#     st.session_state.elevation = 45  # Default Top Right Front

# def save_uploaded_file(uploaded_file):
#     """Save uploaded file temporarily and return the path"""
#     if uploaded_file is not None:
#         tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.stl')
#         tfile.write(uploaded_file.getvalue())
#         return tfile.name
#     return None

# def setup_plotter(mesh, background_color="#e6e9ed", body_color="#b5bec9"):
#     """Create plotter with mesh and edges (done only once)"""
#     plotter = pv.Plotter(off_screen=True, window_size=[600, 600])
#     plotter.background_color = background_color
    
#     # Add mesh with edges
#     edges = mesh.extract_feature_edges(
#         boundary_edges=False,
#         non_manifold_edges=False,
#         feature_angle=45,
#         manifold_edges=False,
#     )
#     plotter.add_mesh(
#         mesh,
#         color=body_color,
#         smooth_shading=True,
#         split_sharp_edges=True,
#         edge_color='black',
#     )
#     plotter.add_mesh(edges, color='black', line_width=2)
    
#     return plotter

# def get_view_image(plotter, azimuth, elevation):
#     """Update camera and get screenshot"""
#     plotter.reset_camera()
#     plotter.camera_position = 'xy'
#     plotter.camera.azimuth = azimuth
#     plotter.camera.elevation = elevation
#     plotter.show(auto_close=False)
#     return plotter.screenshot()

# st.title("STL View Generator")

# # File uploader
# uploaded_file = st.file_uploader("Upload STL file", type=['stl'])

# if uploaded_file:
#     try:
#         # Only set up plotter and mesh once when file is uploaded
#         if st.session_state.plotter is None:
#             st.session_state.mesh_path = save_uploaded_file(uploaded_file)
#             mesh = pv.read(st.session_state.mesh_path)
#             st.session_state.plotter = setup_plotter(mesh)

#         # Create layout with spacing
#         control_col, spacer, image_col, spacer2 = st.columns([1, 0.2, 1, 0.8])

#         with control_col:
#             st.markdown("### View Controls")
            
#             # Preset views
#             selected_preset = st.selectbox("Preset Views", list(PRESET_VIEWS.keys()), 
#                                          index=list(PRESET_VIEWS.keys()).index('Top Right Front'))
#             if selected_preset:
#                 st.session_state.azimuth = PRESET_VIEWS[selected_preset]['azimuth']
#                 st.session_state.elevation = PRESET_VIEWS[selected_preset]['elevation']

#             # View controls
#             st.session_state.azimuth = st.slider("Azimuth", -180, 180, st.session_state.azimuth)
#             st.session_state.elevation = st.slider("Elevation", -90, 90, st.session_state.elevation)

#             # Capture button
#             if st.button("Capture Current View"):
#                 preview_image = get_view_image(st.session_state.plotter, 
#                                             st.session_state.azimuth, 
#                                             st.session_state.elevation)
#                 st.session_state.captured_views.append({
#                     'image': preview_image.copy(),
#                     'timestamp': datetime.now().strftime("%Y%m%d_%H%M%S"),
#                     'azimuth': st.session_state.azimuth,
#                     'elevation': st.session_state.elevation
#                 })
#                 st.success("View captured!")

#         with image_col:
#             preview_image = get_view_image(st.session_state.plotter, 
#                                          st.session_state.azimuth, 
#                                          st.session_state.elevation)
#             st.image(preview_image, caption="Preview", use_container_width=True)

#         # Display captured views
#         if st.session_state.captured_views:
#             st.header("Captured Views")
#             for idx, view in enumerate(st.session_state.captured_views):
#                 cols = st.columns([2, 1])
#                 with cols[0]:
#                     st.image(view['image'], width=300)
#                 with cols[1]:
#                     st.write(f"Azimuth: {view['azimuth']}°")
#                     st.write(f"Elevation: {view['elevation']}°")

#     except Exception as e:
#         st.error(f"Error: {str(e)}")

import streamlit as st
import os
import time
import platform
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import tempfile
import subprocess
from PIL import Image


def is_mac():
    return platform.system() == 'Darwin'


def copy_image_to_clipboard_mac(img_path):
    st.write(f"DEBUG: Copying image to clipboard: {img_path}")
    try:
        applescript = f'''
        set theFile to POSIX file "{img_path}"
        set theImage to (read theFile as JPEG picture)
        set the clipboard to theImage
        '''
        subprocess.run(['osascript', '-e', applescript])
        st.write("DEBUG: Image copied to clipboard successfully")
    except Exception as e:
        st.error(f"Clipboard operation failed: {str(e)}")
        st.write("DEBUG: Continuing despite clipboard error...")


def copy_image_to_clipboard_linux(img_path):
    st.write(f"DEBUG: Copying image to clipboard on Linux")
    try:
        subprocess.run(['xclip', '-selection', 'clipboard', '-t', 'image/png', '-i', img_path])
        st.write("DEBUG: Image copied to clipboard successfully")
    except Exception as e:
        st.error(f"Linux clipboard operation failed: {str(e)}")
        st.write("DEBUG: Continuing despite clipboard error...")


def copy_image_to_clipboard(img_path):
    try:
        if is_mac():
            copy_image_to_clipboard_mac(img_path)
        else:
            copy_image_to_clipboard_linux(img_path)
    except Exception as e:
        st.error(f"Clipboard operation failed but continuing: {str(e)}")
        pass


def setup_chrome_options(temp_dir):
    chrome_options = Options()

    # Headless mode configuration for Linux/Production
    if not is_mac():
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--single-process')

    # Common options
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": temp_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })

    return chrome_options


def run_vizcom_automation(model_image_path, styling_image_path, rendering_prompt,
                          styling_strength, vizcom_username, vizcom_password, progress_bar):
    st.write("DEBUG: Starting Vizcom automation")

    with tempfile.TemporaryDirectory() as temp_dir:
        st.write(f"DEBUG: Created temp directory: {temp_dir}")

        chrome_options = setup_chrome_options(temp_dir)
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        wait = WebDriverWait(driver, 30)
        final_screenshot_path = os.path.join(temp_dir, "final_result.png")

        try:
            # Login process
            st.write("DEBUG: Starting login process")
            driver.get("https://app.vizcom.ai/files/team/2f8f9d59-a5b8-4175-b258-e339144008a5")
            progress_bar.progress(10)

            # Copy model image to clipboard
            copy_image_to_clipboard(model_image_path)
            progress_bar.progress(20)

            # Login
            email_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='email']")))
            email_input.send_keys(vizcom_username)
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.jRuTWx"))).click()
            progress_bar.progress(30)

            time.sleep(3)
            password_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='password']")))
            password_input.send_keys(vizcom_password)
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.jRuTWx"))).click()
            progress_bar.progress(40)

            # Navigation
            st.write("DEBUG: Navigating to studio")
            time.sleep(3)
            wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'New file')]"))).click()
            time.sleep(3)
            wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Start in Studio']"))).click()
            progress_bar.progress(50)

            # Canvas setup
            time.sleep(5)
            wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Landscape']"))).click()
            time.sleep(2)
            wait.until(EC.presence_of_element_located((By.XPATH, "//button[text()='Create']"))).click()
            progress_bar.progress(60)

            # Paste model image
            st.write("DEBUG: Pasting model image")
            time.sleep(3)
            canvas_container = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.cQHQvu")))
            driver.execute_script("arguments[0].click();", canvas_container)
            actions = ActionChains(driver)
            actions.key_down(Keys.COMMAND).send_keys('v').key_up(Keys.COMMAND).perform()
            progress_bar.progress(70)

            # Style settings
            st.write("DEBUG: Applying style settings")
            time.sleep(3)
            add_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.gEjJrb")))
            driver.execute_script("arguments[0].click();", add_button)

            time.sleep(3)
            style_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Style']")))
            driver.execute_script("arguments[0].click();", style_button)
            progress_bar.progress(80)

            # Upload style image
            time.sleep(3)
            upload_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Upload...']")))
            driver.execute_script("arguments[0].click();", upload_button)
            file_input = driver.find_element(By.CSS_SELECTOR, "input[type='file']")
            file_input.send_keys(styling_image_path)

            # Set style strength
            time.sleep(3)
            percentage_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.sc-dBfUQs.gOSsgq")))
            percentage_button.click()
            percentage_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input.sc-kLgxMn.eVooDm")))
            percentage_input.send_keys(styling_strength)
            progress_bar.progress(85)

            # Set prompt and generate
            st.write("DEBUG: Setting prompt and generating")
            prompt_textarea = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "textarea.fmJnQo")))
            prompt_textarea.clear()
            prompt_textarea.send_keys(rendering_prompt)

            time.sleep(3)
            generate_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.sc-gJFNMl.kLShra")))
            driver.execute_script("arguments[0].click();", generate_button)
            progress_bar.progress(90)
            time.sleep(3)
            # Wait for the download button to be enabled using a while loop
            max_wait_time = 120  # Maximum wait time in seconds
            start_time = time.time()
            generation_completed = False

            while time.time() - start_time < max_wait_time and not generation_completed:
                #try:
                download_button = driver.find_element(By.CSS_SELECTOR, "button.sc-gJFNMl.kJmtTh")
                button_html = download_button.get_attribute('outerHTML')
                if "disabled" not in button_html:
                    st.write("DEBUG: Generation appears to be complete (stable state detected)")
                    generation_completed = True
                    break
                else:
                    time.sleep(5)

            progress_bar.progress(100)

            # Take a screenshot
            driver.save_screenshot(final_screenshot_path)

            # Process the screenshot to crop the result area
            with Image.open(final_screenshot_path) as img:
                # Crop to the Vizcom result area
                # These coordinates focus on the center area where the generated image appears
                width, height = img.size
                left = width // 4
                top = height // 4
                right = width * 3 // 4
                bottom = height * 3 // 4
                cropped_img = img.crop((left, top, right, bottom))

                # Save the cropped image
                cropped_path = os.path.join(os.path.dirname(final_screenshot_path), "cropped_result.png")
                cropped_img.save(cropped_path)

                # Read the cropped image
                with open(cropped_path, 'rb') as f:
                    screenshot_bytes = f.read()

            progress_bar.progress(100)
            return screenshot_bytes

        except Exception as e:
            st.error(f"Automation error: {str(e)}")
            st.write(f"DEBUG: Error occurred at URL: {driver.current_url}")
            error_screenshot = os.path.join(temp_dir, "error.png")
            driver.save_screenshot(error_screenshot)
            with open(error_screenshot, 'rb') as f:
                return f.read()
        finally:
            driver.quit()


def main():
    st.title("Vizcom Automation Tool")

    # Environment information
    with st.expander("Environment Information"):
        st.write(f"Running on: {platform.system()}")
        st.write(f"Platform: {platform.platform()}")

    # File uploaders
    model_image = st.file_uploader("Upload Model Image", type=['png', 'jpg', 'jpeg'])
    styling_image = st.file_uploader("Upload Styling Image", type=['png', 'jpg', 'jpeg'])

    # Input fields
    col1, col2 = st.columns(2)
    with col1:
        rendering_prompt = st.text_input("Rendering Prompt")
        styling_strength = st.text_input("Styling Strength (0-100)", "85")
    with col2:
        vizcom_username = st.text_input("Vizcom Username")
        vizcom_password = st.text_input("Vizcom Password", type="password")

    if st.button("Run Automation") and model_image and styling_image:
        # Save uploaded files temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_model:
            tmp_model.write(model_image.getvalue())
            model_path = tmp_model.name

        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_style:
            tmp_style.write(styling_image.getvalue())
            style_path = tmp_style.name

        try:
            progress_bar = st.progress(0)
            st.write("Starting automation process...")

            screenshot_bytes = run_vizcom_automation(
                model_path,
                style_path,
                rendering_prompt,
                styling_strength,
                vizcom_username,
                vizcom_password,
                progress_bar
            )

            if screenshot_bytes:
                st.write("Automation completed!")
                st.image(screenshot_bytes, caption="Final Result", use_column_width=True)

                # Add download button
                st.download_button(
                    label="Download Result",
                    data=screenshot_bytes,
                    file_name="vizcom_result.png",
                    mime="image/png"
                )
            else:
                st.error("Failed to generate result")

        except Exception as e:
            st.error(f"Process failed: {str(e)}")

        finally:
            # Cleanup temporary files
            os.unlink(model_path)
            os.unlink(style_path)


if __name__ == "__main__":
    main()
