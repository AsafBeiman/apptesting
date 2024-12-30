import streamlit as st
import pyvista as pv
import tempfile
import os
from datetime import datetime

# Initialize PyVista
pv.start_xvfb()
st.set_page_config(layout="wide")

# Initialize session state
if 'plotter' not in st.session_state:
    st.session_state.plotter = None
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

def setup_plotter(mesh, background_color="#e6e9ed", body_color="#b5bec9"):
    """Create plotter with mesh and edges (done only once)"""
    plotter = pv.Plotter(off_screen=True, window_size=[400, 400])
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
    
    # Initial camera setup
    plotter.camera.position = (0, 0, 1)
    plotter.camera.up = (0, 1, 0)
    plotter.reset_camera()
    
    return plotter

def get_view_image(plotter, azimuth, elevation):
    """Update camera and get screenshot"""
    plotter.camera.azimuth = azimuth
    plotter.camera.elevation = elevation
    plotter.show(auto_close=False)  # Render the scene
    return plotter.screenshot()

st.title("STL View Generator")

# File uploader
uploaded_file = st.file_uploader("Upload STL file", type=['stl'])

if uploaded_file:
    try:
        # Only set up plotter and mesh once when file is uploaded
        if st.session_state.plotter is None:
            # Save file
            st.session_state.mesh_path = save_uploaded_file(uploaded_file)
            # Read STL and setup plotter
            mesh = pv.read(st.session_state.mesh_path)
            st.session_state.plotter = setup_plotter(mesh)
        
        # Layout
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # View controls
            azimuth = st.slider("Azimuth", -180, 180, 0)
            elevation = st.slider("Elevation", -90, 90, 0)
            
            # Generate and show preview using existing plotter
            preview_image = get_view_image(st.session_state.plotter, azimuth, elevation)
            st.image(preview_image, caption="Preview")
        
        with col2:
            if st.button("Capture Current View"):
                st.session_state.captured_views.append({
                    'image': preview_image.copy(),  # Make a copy of the current image
                    'timestamp': datetime.now().strftime("%Y%m%d_%H%M%S"),
                    'azimuth': azimuth,
                    'elevation': elevation
                })
                st.success("View captured!")

        # Display captured views
        if st.session_state.captured_views:
            st.header("Captured Views")
            for idx, view in enumerate(st.session_state.captured_views):
                cols = st.columns([2, 1, 1])
                with cols[0]:
                    st.image(view['image'], width=200)
                with cols[1]:
                    st.write(f"Azimuth: {view['azimuth']}°")
                    st.write(f"Elevation: {view['elevation']}°")
                with cols[2]:
                    if st.button(f"Delete View {idx}"):
                        st.session_state.captured_views.pop(idx)
                        st.rerun()

        if st.sidebar.button("Clear All"):
            if st.session_state.mesh_path and os.path.exists(st.session_state.mesh_path):
                os.unlink(st.session_state.mesh_path)
            if st.session_state.plotter is not None:
                st.session_state.plotter.close()
            st.session_state.plotter = None
            st.session_state.mesh_path = None
            st.session_state.captured_views = []
            st.rerun()

    except Exception as e:
        st.error(f"Error: {str(e)}")
