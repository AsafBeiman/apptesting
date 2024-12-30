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

# Define preset views
PRESET_VIEWS = {
    'Front': {'azimuth': 0, 'elevation': 0},
    'Right': {'azimuth': 90, 'elevation': 0},
    'Left': {'azimuth': -90, 'elevation': 0},
    'Back': {'azimuth': 180, 'elevation': 0},
    'Top': {'azimuth': 0, 'elevation': 90},
    'Iso Right Front': {'azimuth': 45, 'elevation': 45},
    'Iso Right Back': {'azimuth': 135, 'elevation': 45},
    'Iso Left Front': {'azimuth': -45, 'elevation': 45},
    'Iso Left Back': {'azimuth': -135, 'elevation': 45},
}

def save_uploaded_file(uploaded_file):
    """Save uploaded file temporarily and return the path"""
    if uploaded_file is not None:
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.stl')
        tfile.write(uploaded_file.getvalue())
        return tfile.name
    return None

def setup_plotter(plotter, mesh, body_color, background_color):
    """Setup plotter with consistent settings"""
    plotter.background_color = background_color
    edges = mesh.extract_feature_edges(
        boundary_edges=False,
        non_manifold_edges=False,
        feature_angle=45,
        manifold_edges=False,
    )
    plotter.add_mesh(mesh, color=body_color, smooth_shading=True, 
                    split_sharp_edges=True, edge_color='black')
    plotter.add_mesh(edges, color='black', line_width=2)
    return plotter

def capture_view(plotter, mesh, body_color, background_color):
    """Capture current view and return image data"""
    # Create a new plotter for the screenshot with off_screen=True
    temp_plotter = pv.Plotter(off_screen=True, window_size=plotter.window_size)
    
    # Set up the temp plotter exactly like the main plotter
    setup_plotter(temp_plotter, mesh, body_color, background_color)
    
    # Copy camera position and orientation
    temp_plotter.camera = plotter.camera.copy()
    temp_plotter.camera.reset_clipping_range()

    # Create a temporary file for the screenshot
    temp_img = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    temp_plotter.screenshot(temp_img.name)

    # Read the image and convert to base64
    with open(temp_img.name, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()

    # Clean up
    os.unlink(temp_img.name)
    temp_plotter.close()

    return encoded_string

def main():
    st.title("STL Viewer and Capture")

    # Initialize session state for captured images
    if 'captured_images' not in st.session_state:
        st.session_state.captured_images = []
    if 'plotter' not in st.session_state:
        st.session_state.plotter = None

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

        # Read STL file
        mesh = pv.read(file_path)

        # Create plotter for interactive viewing
        plotter = pv.Plotter(window_size=[800, 600])
        setup_plotter(plotter, mesh, body_color, background_color)
        plotter.reset_camera()
        
        # Store plotter in session state
        st.session_state.plotter = plotter
        
        # Create columns for preset view buttons
        st.subheader("Preset Views")
        button_cols = st.columns(5)  # 5 buttons per row
        
        for idx, (view_name, angles) in enumerate(PRESET_VIEWS.items()):
            col_idx = idx % 5
            with button_cols[col_idx]:
                if st.button(view_name):
                    plotter.reset_camera()
                    plotter.camera.azimuth = angles['azimuth']
                    plotter.camera.elevation = angles['elevation']

        # Create two columns for the viewer and capture button
        col1, col2 = st.columns([4, 1])

        with col1:
            # Display the interactive viewer
            stpyvista(plotter, key="stl_viewer")

        with col2:
            # Capture button
            if st.button("Capture View"):
                # Capture the current view
                img_data = capture_view(plotter, mesh, body_color, background_color)
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
