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
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import tempfile
import subprocess
from PIL import Image

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
    from seleniumbase import Driver
    
    options = Options()
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--window-size=1920,1080")
    
    try:
        driver = Driver(uc=True, options=options)  # Using undetected-chromedriver
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

    # [Rest of the VizcomAutomation class methods remain the same]

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
