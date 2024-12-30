import streamlit as st
import pyvista as pv
from stpyvista import stpyvista
import tempfile
import os
from pathlib import Path
import base64
from datetime import datetime

# Initialize PyVista and Streamlit settings
pv.start_xvfb()
st.set_page_config(layout="wide")

def save_uploaded_file(uploaded_file):
    """Save uploaded file temporarily and return the path"""
    if uploaded_file is not None:
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.stl')
        tfile.write(uploaded_file.getvalue())
        return tfile.name
    return None

def capture_view(plotter):
    """Capture current view and return image data"""
    # Create a temporary file for the screenshot
    temp_img = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    plotter.screenshot(temp_img.name)
    
    # Read the image and convert to base64
    with open(temp_img.name, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    
    # Clean up
    os.unlink(temp_img.name)
    
    return encoded_string

def main():
    st.title("STL Viewer and Capture")
    
    # Initialize session state for captured images
    if 'captured_images' not in st.session_state:
        st.session_state.captured_images = []
    
    # File uploader
    uploaded_file = st.file_uploader("Upload STL file", type=['stl'])
    
    if uploaded_file:
        # Save file temporarily
        file_path = save_uploaded_file(uploaded_file)
        
        # Sidebar controls
        st.sidebar.header("View Settings")
        
        # Color pickers
        background_color = st.sidebar.color_picker("Background Color", "#e6e9ed")
        body_color = st.sidebar.color_picker("Body Color", "#b5bec9")
        
        # Create plotter
        plotter = pv.Plotter(window_size=[800, 600])
        plotter.background_color = background_color
        
        # Read STL file
        mesh = pv.read(file_path)
        
        # Add mesh to plotter
        plotter.add_mesh(mesh, color=body_color, show_edges=True, edge_color='black')
        
        # Reset camera
        plotter.reset_camera()
        
        # Create two columns for the viewer and capture button
        col1, col2 = st.columns([4, 1])
        
        with col1:
            # Display the interactive viewer
            stpyvista(plotter, key="stl_viewer")
        
        with col2:
            # Capture button
            if st.button("Capture View"):
                # Capture the current view
                img_data = capture_view(plotter)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                st.session_state.captured_images.append({
                    'data': img_data,
                    'timestamp': timestamp
                })
                st.success("View captured!")
        
        # Display captured images
        if st.session_state.captured_images:
            st.header("Captured Views")
            
            # Create a grid of images
            cols = st.columns(3)
            for idx, img in enumerate(st.session_state.captured_images):
                col_idx = idx % 3
                with cols[col_idx]:
                    st.image(
                        f"data:image/png;base64,{img['data']}", 
                        caption=f"View {img['timestamp']}",
                        use_column_width=True
                    )
                    
                    # Add download button for each image
                    download_btn = f"""
                    <a href="data:image/png;base64,{img['data']}" 
                       download="view_{img['timestamp']}.png">
                        Download Image
                    </a>
                    """
                    st.markdown(download_btn, unsafe_allow_html=True)
        
        # Cleanup
        os.unlink(file_path)

if __name__ == "__main__":
    main()
