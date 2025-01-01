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

# import streamlit as st
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from webdriver_manager.core.os_manager import ChromeType
# from PIL import Image
# import io

# @st.cache_resource
# def get_driver():
#     options = Options()
#     options.add_argument("--disable-gpu")
#     options.add_argument("--headless")
#     # Set a specific window size for consistent screenshots
#     options.add_argument("--window-size=1920,1080")
    
#     return webdriver.Chrome(
#         service=Service(
#             ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
#         ),
#         options=options,
#     )

# # Get the driver
# driver = get_driver()

# # Navigate to the website
# driver.get("http://example.com")

# # Take screenshot
# screenshot = driver.get_screenshot_as_png()

# # Convert the screenshot to an image that Streamlit can display
# image = Image.open(io.BytesIO(screenshot))

# # Display the screenshot
# st.image(image, caption='Website Screenshot', use_column_width=True)

# # Don't forget to quit the driver
# driver.quit()

# import streamlit as st
# import os
# import time
# import platform
# import tempfile
# import subprocess
# from PIL import Image
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.chrome import ChromeDriverManager
# from webdriver_manager.core.os_manager import ChromeType
# import io

# # @st.cache_resource
# # def get_driver():
# #     options = Options()
# #     options.add_argument("--disable-gpu")
# #     options.add_argument("--headless")
# #     # Set a specific window size for consistent screenshots
# #     options.add_argument("--window-size=1920,1080")
    
# #     return webdriver.Chrome(
# #         service=Service(
# #             ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
# #         ),
# #         options=options,
# #     )
# def is_mac():
#     return platform.system() == 'Darwin'

# @st.cache_resource
# def get_driver():
#     if not is_mac():
#         options = Options()
    
#         # Basic headless setup
#         options.add_argument("--headless=new")
#         options.add_argument("--window-size=1920,1080")
        
#         # Memory-related options to prevent crashes
#         options.add_argument("--no-sandbox")  # Less secure but more stable
#         options.add_argument("--disable-dev-shm-usage")  # Use /tmp instead of /dev/shm
        
#         # Additional stability options
#         options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
#         options.add_argument("--ignore-certificate-errors")  # Handle SSL/HTTPS issues
#         options.add_argument("--remote-debugging-port=9222")  # Enable debugging if needed
        
#         # Memory management
#         options.add_argument("--start-maximized")  # Start maximized to ensure consistent viewport
#         options.add_argument("--disable-extensions")  # Disable extensions for stability
    

#         return webdriver.Chrome(
#             service=Service(
#                 ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
#             ),
#             options=options,
#         )
#     else:
#         chrome_options = Options()
#         chrome_options.add_argument("--headless")  # Run in background
#         chrome_options.add_argument("--no-sandbox")
#         chrome_options.add_argument("--disable-dev-shm-usage")

#         # Set up the WebDriver
#         service = Service(ChromeDriverManager().install())
#         driver = webdriver.Chrome(service=service, options=chrome_options)
#         driver.set_window_size(1920, 1080)
#         return driver

# # # Get the driver
# # driver = get_driver()

# # # Navigate to the website
# # driver.get("http://example.com")

# # # Take screenshot
# # screenshot = driver.get_screenshot_as_png()

# # # Convert the screenshot to an image that Streamlit can display
# # image = Image.open(io.BytesIO(screenshot))

# # # Display the screenshot
# # st.image(image, caption='Website Screenshot', use_column_width=True)

# # # Don't forget to quit the driver
# # driver.quit()
# def run_automation(model_image_path, styling_image_path, rendering_prompt,
#                    styling_strength, vizcom_username, vizcom_password, progress_bar):
#     driver = get_driver()
#     wait = WebDriverWait(driver, 30)
#     # Navigate to the website
#     driver.get("http://app.vizcom.ai/auth")
#     time.sleep(3)
#     img0 = driver.get_screenshot_as_png()
#     st.image(img0, caption="img0")
#     email_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='email']")))
#     email_input.send_keys(vizcom_username)
#     time.sleep(2)
#     img1 = driver.get_screenshot_as_png()
#     st.image(img1, caption="img1")
#     wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.jRuTWx"))).click()
#     time.sleep(2)
#     img2 = driver.get_screenshot_as_png()
#     st.image(img2, caption="img2")
#     wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='password']"))).send_keys(
#         vizcom_password)
#     wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.jRuTWx"))).click()
#     # time.sleep(3)
#     # img3 = driver.get_screenshot_as_png()
#     # st.image(img3, caption="img3")
#     # time.sleep(3)
#     # wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'New file')]"))).click()
#     # time.sleep(2)
#     # wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Start in Studio']"))).click()
#     # time.sleep(5)
#     # wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Landscape']"))).click()
#     # time.sleep(2)
#     # img7 = driver.get_screenshot_as_png()
#     # st.image(img7, caption="img1")
#     driver.quit()
#     return img2

# def main():
#     st.set_page_config(layout="wide")
#     st.title("Vizcom AI Automation - STL Styling")

#     # Create two columns for inputs
#     col1, col2 = st.columns(2)

#     with col1:
#         st.subheader("Images")
#         # model_image = st.file_uploader("Upload Model Image", type=['png', 'jpg', 'jpeg'])
#         # if model_image:
#         #     st.image(model_image, caption="Model Image")

#         # styling_image = st.file_uploader("Upload Style Image", type=['png', 'jpg', 'jpeg'])
#         # if styling_image:
#         #     st.image(styling_image, caption="Style Image")

#     with col2:
#         st.subheader("Settings")
#         vizcom_username = st.text_input("Vizcom Username (Email)")
#         vizcom_password = st.text_input("Vizcom Password", type="password")
#         # rendering_prompt = st.text_area("Rendering Prompt")
#         # styling_strength = st.slider("Style Strength", 0, 100, 85)

#     # Add a process button
#     if st.button("Generate Image"):
#         # if not all([model_image, styling_image, vizcom_username, vizcom_password, rendering_prompt]):
#         #     st.error("Please fill in all required fields")
#         #     return

#         # Create progress bar
#         # progress_bar = st.progress(0)
#         st.write("Starting automation process...")

#         try:
#             # # Save uploaded images to temporary files
#             # with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_model:
#             #     tmp_model.write(model_image.getvalue())
#             #     model_path = tmp_model.name

#             # with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_style:
#             #     tmp_style.write(styling_image.getvalue())
#             #     style_path = tmp_style.name

#             # Run the automation
#             result = run_automation(
#                 None, # model_path,
#                 None, # style_path,
#                 None, # rendering_prompt,
#                 None, # styling_strength,
#                 vizcom_username,
#                 vizcom_password,
#                 None, # progress_bar
#             )

#             if result:
#                 st.success("Image generated successfully!")
#                 st.image(result, caption="Generated Result")

#                 # Add download button
#                 st.download_button(
#                     label="Download Result",
#                     data=result,
#                     file_name="vizcom_result.png",
#                     mime="image/png"
#                 )
#             else:
#                 st.error("Failed to generate image")

#         except Exception as e:
#             st.error(f"An error occurred: {str(e)}")
#             st.write("Please check your inputs and try again")

#         # finally:
#         #     # Clean up temporary files
#         #     if 'model_path' in locals():
#         #         os.unlink(model_path)
#         #     if 'style_path' in locals():
#         #         os.unlink(style_path)


# if __name__ == "__main__":
#     main()

# firefoxtest
import streamlit as st
import os
import time
import platform
import tempfile
import subprocess
from PIL import Image
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.firefox import GeckoDriverManager

options = Options()
options.add_argument("--headless")
options.add_argument("--width=1920")
options.add_argument("--height=1080")

try:
    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=options)
    # Explicitly set window size
    driver.set_window_size(1920, 1080)
    
    st.write("Navigating to website...")
    driver.get("http://app.vizcom.ai/auth")
    
    # Wait for page load
    wait = WebDriverWait(driver, 60)
    # Wait for a specific element that indicates the page is loaded
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    
    # Add a small delay to ensure complete rendering
    time.sleep(5)
    
    # Log the page source to debug
    st.write("Page source length:", len(driver.page_source))
    
    # Take screenshot
    img7 = driver.get_screenshot_as_png()
    
    # Convert to PIL Image to check dimensions
    from PIL import Image
    import io
    img_pil = Image.open(io.BytesIO(img7))
    st.write("Screenshot dimensions:", img_pil.size)
    
    # Display the image
    st.image(img7)
    
except Exception as e:
    st.error(f"Error: {str(e)}")
finally:
    driver.quit()

# def is_mac():
#     return platform.system() == 'Darwin'


# @st.cache_resource
# def get_driver():
#     options = Options()
#     options.add_argument("--headless")
    
#     if platform.system() == 'Darwin':  # macOS
#         # Mac-specific settings
#         options.binary_location = '/Applications/Firefox.app/Contents/MacOS/firefox'
#     else:
#         # Linux/Cloud settings
#         options.add_argument("--no-sandbox")
#         options.add_argument("--disable-dev-shm-usage")
    
#     options.add_argument("--width=1920")
#     options.add_argument("--height=1080")
    
#     try:
#         service = Service(GeckoDriverManager().install())
#         driver = webdriver.Firefox(service=service, options=options)
#         driver.set_window_size(1920, 1080)
#         return driver
#     except Exception as e:
#         st.error(f"Failed to initialize Firefox driver: {str(e)}")
#         st.info("If you're on Mac, make sure Firefox is installed in /Applications")
#         raise e
    
#     if not is_mac():
#         # Linux/Windows specific settings
#         options.add_argument("--width=1920")
#         options.add_argument("--height=1080")
#     else:
#         # Mac specific settings
#         options.add_argument("--no-sandbox")
#         options.add_argument("--disable-dev-shm-usage")

#     # Set up the Firefox WebDriver
#     service = Service(GeckoDriverManager().install())
#     driver = webdriver.Firefox(service=service, options=options)
#     driver.set_window_size(1920, 1080)
#     return driver


# def run_automation():
#     driver = get_driver()
#     wait = WebDriverWait(driver, 60)  # Increased wait time to 60 seconds
    
#     #try:
#     # Navigate to the website
#     st.write("Navigating to website...")
#     driver.get("http://app.vizcom.ai/auth")
#     time.sleep(7)  # Increased initial wait time
#     img7 = driver.get_screenshot_as_png()
#     st.image(img7)
#     # try:
#     #     st.write("Logging in...")
#     #     # Wait for and handle login form
#     #     email_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")))
#     #     email_input.clear()
#     #     email_input.send_keys(vizcom_username)
#     #     progress_bar.progress(20)
        
#     #     # Use JavaScript click for more reliability
#     #     login_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.jRuTWx")))
#     #     driver.execute_script("arguments[0].click();", login_button)
#     #     time.sleep(5)  # Increased wait time
        
#     #     progress_bar.progress(30)
#     #     password_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']")))
#     #     password_input.clear()
#     #     password_input.send_keys(vizcom_password)
        
#     #     submit_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.jRuTWx")))
#     #     driver.execute_script("arguments[0].click();", submit_button)
#     #     time.sleep(5)  # Increased wait time
#     # except Exception as e:
#     #     st.error(f"Login failed: {str(e)}")
#     #     driver.quit()
#     #     raise e
#     # progress_bar.progress(40)
#     # try:
#     #     st.write("Navigating to studio...")
#     #     time.sleep(5)  # Wait for page load
#     #     new_file_link = wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'New file')]")))
#     #     driver.execute_script("arguments[0].click();", new_file_link)
#     #     time.sleep(3)
        
#     #     start_studio = wait.until(EC.presence_of_element_located((By.XPATH, "//span[text()='Start in Studio']")))
#     #     driver.execute_script("arguments[0].click();", start_studio)
#     #     time.sleep(7)  # Increased wait time for studio load
        
#     #     landscape = wait.until(EC.presence_of_element_located((By.XPATH, "//span[text()='Landscape']")))
#     #     driver.execute_script("arguments[0].click();", landscape)
#     #     time.sleep(3)
#     # except Exception as e:
#     #     st.error(f"Failed to navigate to studio: {str(e)}")
#     #     driver.quit()
#     #     raise e
#     # progress_bar.progress(50)
#     # upload_image_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Upload an image']")))
#     # driver.execute_script("arguments[0].click();", upload_image_button)
#     # image_file_input = driver.find_element(By.CSS_SELECTOR, "input[type='file']")
#     # image_file_input.send_keys(model_image_path)
#     # time.sleep(1)
#     # progress_bar.progress(60)
#     # time.sleep(2)
#     # add_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.gEjJrb")))
#     # driver.execute_script("arguments[0].click();", add_button)
#     # time.sleep(2)
#     # style_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Style']")))
#     # driver.execute_script("arguments[0].click();", style_button)
#     # time.sleep(2)
#     # upload_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Upload...']")))
#     # driver.execute_script("arguments[0].click();", upload_button)
#     # file_input = driver.find_element(By.CSS_SELECTOR, "input[type='file']")
#     # file_input.send_keys(styling_image_path)
#     # time.sleep(2)
#     # progress_bar.progress(70)
#     # percentage_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.sc-dBfUQs.gOSsgq")))
#     # percentage_button.click()
#     # time.sleep(0.5)  # Short wait for the input to become active
#     # percentage_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input.sc-kLgxMn.eVooDm")))
#     # percentage_input.send_keys(styling_strength)
#     # time.sleep(2)
#     # progress_bar.progress(75)
#     # # Step 9: Enter text in prompt textarea
#     # prompt_textarea = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "textarea.fmJnQo")))
#     # prompt_textarea.clear()
#     # prompt_textarea.send_keys(rendering_prompt)
#     # progress_bar.progress(80)
#     # time.sleep(2)
#     # # Step 10: Click Generate button and wait
#     # generate_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.sc-gJFNMl.kLShra")))
#     # driver.execute_script("arguments[0].click();", generate_button)
#     # progress_bar.progress(90)
#     # start_time = time.time()
#     # while time.time() - start_time < 120:  # 2 minute timeout
#     #     try:
#     #         add_button = driver.find_element(By.CSS_SELECTOR, "button.sc-gJFNMl.kJmtTh")
#     #         button_html = add_button.get_attribute('outerHTML')
#     #         if "disabled" not in button_html:
#     #             st.write("Generation complete")
#     #             break
#     #     except Exception as e:
#     #         st.write(f"DEBUG: Waiting for generation... {str(e)}")
#     #     time.sleep(5)
#     # time.sleep(1)
#     # img7 = driver.get_screenshot_as_png()
#     # time.sleep(1)
#     # progress_bar.progress(100)
#     # # Don't forget to quit the driver
#     driver.quit()
#     return img7


# def main():
#     st.set_page_config(layout="wide")
#     st.title("Vizcom AI Automation - STL Styling")
#     result = run_automation()

#     if result:
#         st.success("Image generated successfully!")
#         st.image(result, caption="Generated Result")
#     # Create two columns for inputs
#     # col1, col2 = st.columns(2)

#     # with col1:
#     #     st.subheader("Images")
#     #     model_image = st.file_uploader("Upload Model Image", type=['png', 'jpg', 'jpeg'])
#     #     if model_image:
#     #         st.image(model_image, caption="Model Image")

#     #     styling_image = st.file_uploader("Upload Style Image", type=['png', 'jpg', 'jpeg'])
#     #     if styling_image:
#     #         st.image(styling_image, caption="Style Image")

#     # with col2:
#     #     st.subheader("Settings")
#     #     vizcom_username = st.text_input("Vizcom Username (Email)")
#     #     vizcom_password = st.text_input("Vizcom Password", type="password")
#     #     rendering_prompt = st.text_area("Rendering Prompt")
#     #     styling_strength = st.slider("Style Strength", 0, 100, 85)

#     # # Add a process button
#     # if st.button("Generate Image"):
#     #     if not all([model_image, styling_image, vizcom_username, vizcom_password, rendering_prompt]):
#     #         st.error("Please fill in all required fields")
#     #         return

#     #     # Create progress bar
#     #     progress_bar = st.progress(0)
#     #     st.write("Starting automation process...")

#     #     try:
#     #         # Save uploaded images to temporary files
#     #         with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_model:
#     #             tmp_model.write(model_image.getvalue())
#     #             model_path = tmp_model.name

#     #         with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_style:
#     #             tmp_style.write(styling_image.getvalue())
#     #             style_path = tmp_style.name

#     #         # Run the automation
#     #         result = run_automation(
#     #             model_path,
#     #             style_path,
#     #             rendering_prompt,
#     #             styling_strength,
#     #             vizcom_username,
#     #             vizcom_password,
#     #             progress_bar
#     #         )

#     #         if result:
#     #             st.success("Image generated successfully!")
#     #             st.image(result, caption="Generated Result")

#     #             # Add download button
#     #             st.download_button(
#     #                 label="Download Result",
#     #                 data=result,
#     #                 file_name="vizcom_result.png",
#     #                 mime="image/png"
#     #             )
#     #         else:
#     #             st.error("Failed to generate image")

#     #     except Exception as e:
#     #         st.error(f"An error occurred: {str(e)}")
#     #         st.write("Please check your inputs and try again")

#     #     finally:
#     #         # Clean up temporary files
#     #         if 'model_path' in locals():
#     #             os.unlink(model_path)
#     #         if 'style_path' in locals():
#     #             os.unlink(style_path)


# if __name__ == "__main__":
#     main()
