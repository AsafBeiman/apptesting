import streamlit as st
import pyvista as pv
import tempfile
import os
from pathlib import Path
from stpyvista import stpyvista
import base64
from datetime import datetime

# Initialize PyVista and Streamlit settings
pv.start_xvfb()
st.set_page_config(layout="wide")

# Initialize session state for mesh and camera
if 'mesh_path' not in st.session_state:
    st.session_state.mesh_path = None
if 'captured_views' not in st.session_state:
    st.session_state.captured_views = []

def save_uploaded_file(uploaded_file):
    """Save uploaded file temporarily and return the path"""
    if uploaded_file is not None:
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.stl')
        tfile.write(uploaded_file.getvalue())
        return tfile.name
    return None

def setup_plotter(mesh, azimuth, elevation, background_color="#e6e9ed", body_color="#b5bec9", window_size=[400, 400], off_screen=False):
    """Set up a plotter with given parameters"""
    plotter = pv.Plotter(off_screen=off_screen, window_size=window_size)
    plotter.background_color = background_color
    
    # Add mesh with edges
    edges = mesh.extract_feature_edges(
        boundary_edges=False,
        non_manifold_edges=False,
        feature_angle=45,
        manifold_edges=False,
    )
    plotter.add_mesh(
        mesh,
        color=body_color,
        smooth_shading=True,
        split_sharp_edges=True,
        edge_color='black'
    )
    plotter.add_mesh(edges, color='black', line_width=2)
    
    # Set camera position
    plotter.camera.position = (0, 0, 1)
    plotter.camera.up = (0, 1, 0)
    plotter.reset_camera()
    plotter.camera.azimuth = azimuth
    plotter.camera.elevation = elevation
    
    return plotter

st.title("STL Viewer with View Control")

# File uploader
uploaded_file = st.file_uploader("Upload STL file", type=['stl'])

if uploaded_file:
    # Save file if new
    if st.session_state.mesh_path is None:
        st.session_state.mesh_path = save_uploaded_file(uploaded_file)
    
    try:
        # Read STL once
        mesh = pv.read(st.session_state.mesh_path)
        
        # Camera controls in sidebar
        st.sidebar.header("Camera Control")
        azimuth = st.sidebar.slider("Azimuth", -180, 180, 0, key="azimuth")
        elevation = st.sidebar.slider("Elevation", -90, 90, 0, key="elevation")
        
        # Create layout
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Interactive viewer
            plotter = setup_plotter(mesh, azimuth, elevation)
            stpyvista(plotter, key="stl_viewer")
        
        with col2:
            if st.button("Capture View"):
                # Create off-screen plotter with same parameters
                off_plotter = setup_plotter(mesh, azimuth, elevation, off_screen=True)
                off_plotter.show(auto_close=False)
                
                # Save screenshot
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                st.session_state.captured_views.append({
                    'image': off_plotter.screenshot(),
                    'timestamp': timestamp,
                    'azimuth': azimuth,
                    'elevation': elevation
                })
                off_plotter.close()
                st.success("View captured!")

        # Display captured views
        if st.session_state.captured_views:
            st.header("Captured Views")
            for idx, view in enumerate(st.session_state.captured_views):
                cols = st.columns(4)
                with cols[0]:
                    st.image(view['image'], width=200)
                with cols[1]:
                    st.write(f"Timestamp: {view['timestamp']}")
                with cols[2]:
                    st.write(f"Azimuth: {view['azimuth']}°\nElevation: {view['elevation']}°")
                with cols[3]:
                    if st.button(f"Delete View {idx}"):
                        st.session_state.captured_views.pop(idx)
                        st.rerun()

    except Exception as e:
        st.error(f"Error: {str(e)}")

# Clear button
if st.sidebar.button("Clear All"):
    if st.session_state.mesh_path and os.path.exists(st.session_state.mesh_path):
        os.unlink(st.session_state.mesh_path)
    st.session_state.mesh_path = None
    st.session_state.captured_views = []
    st.rerun()
