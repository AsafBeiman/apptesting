import streamlit as st
import pyvista as pv
import tempfile
import os
from datetime import datetime

# Initialize PyVista
pv.start_xvfb()
st.set_page_config(layout="wide")

# Preset views
PRESET_VIEWS = {
    'Front': {'azimuth': 0, 'elevation': 0},
    'Right': {'azimuth': 90, 'elevation': 0},
    'Left': {'azimuth': -90, 'elevation': 0},
    'Back': {'azimuth': 180, 'elevation': 0},
    'Top': {'azimuth': 0, 'elevation': 90},
    'Top Right Front': {'azimuth': 45, 'elevation': 45},
    'Top Right Back': {'azimuth': 135, 'elevation': 45},
    'Top Left Front': {'azimuth': -45, 'elevation': 45},
    'Top Left Back': {'azimuth': -135, 'elevation': 45},
    'Bottom Right Front': {'azimuth': 45, 'elevation': -45},
    'Bottom Right Back': {'azimuth': 135, 'elevation': -45},
    'Bottom Left Front': {'azimuth': -45, 'elevation': -45},
    'Bottom Left Back': {'azimuth': -135, 'elevation': -45},
}

# Initialize session state
if 'plotter' not in st.session_state:
    st.session_state.plotter = None
if 'mesh_path' not in st.session_state:
    st.session_state.mesh_path = None
if 'captured_views' not in st.session_state:
    st.session_state.captured_views = []
if 'azimuth' not in st.session_state:
    st.session_state.azimuth = 45  # Default Top Right Front
if 'elevation' not in st.session_state:
    st.session_state.elevation = 45  # Default Top Right Front

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
    
    return plotter

def get_view_image(plotter, azimuth, elevation):
    """Update camera and get screenshot"""
    plotter.reset_camera()
    plotter.camera_position = 'xy'
    plotter.camera.azimuth = azimuth
    plotter.camera.elevation = elevation
    plotter.show(auto_close=False)
    return plotter.screenshot()

st.title("STL View Generator")

# File uploader
uploaded_file = st.file_uploader("Upload STL file", type=['stl'])

if uploaded_file:
    try:
        # Only set up plotter and mesh once when file is uploaded
        if st.session_state.plotter is None:
            st.session_state.mesh_path = save_uploaded_file(uploaded_file)
            mesh = pv.read(st.session_state.mesh_path)
            st.session_state.plotter = setup_plotter(mesh)

        # Create two columns for controls and image
        control_col, image_col = st.columns([1, 2])

        with control_col:
            st.markdown("### View Controls")
            
            # Preset views
            selected_preset = st.selectbox("Preset Views", list(PRESET_VIEWS.keys()), 
                                         index=list(PRESET_VIEWS.keys()).index('Top Right Front'))
            if selected_preset:
                st.session_state.azimuth = PRESET_VIEWS[selected_preset]['azimuth']
                st.session_state.elevation = PRESET_VIEWS[selected_preset]['elevation']

            # View controls
            st.session_state.azimuth = st.slider("Azimuth", -180, 180, st.session_state.azimuth)
            st.session_state.elevation = st.slider("Elevation", -90, 90, st.session_state.elevation)

            # Capture button
            if st.button("Capture Current View"):
                preview_image = get_view_image(st.session_state.plotter, 
                                            st.session_state.azimuth, 
                                            st.session_state.elevation)
                st.session_state.captured_views.append({
                    'image': preview_image.copy(),
                    'timestamp': datetime.now().strftime("%Y%m%d_%H%M%S"),
                    'azimuth': st.session_state.azimuth,
                    'elevation': st.session_state.elevation
                })
                st.success("View captured!")

        with image_col:
            # Generate and show preview using existing plotter
            preview_image = get_view_image(st.session_state.plotter, 
                                         st.session_state.azimuth, 
                                         st.session_state.elevation)
            st.image(preview_image, caption="Preview", use_column_width=True)

        # Display captured views
        if st.session_state.captured_views:
            st.header("Captured Views")
            for idx, view in enumerate(st.session_state.captured_views):
                cols = st.columns([2, 1])
                with cols[0]:
                    st.image(view['image'], width=200)
                with cols[1]:
                    st.write(f"Azimuth: {view['azimuth']}°")
                    st.write(f"Elevation: {view['elevation']}°")

    except Exception as e:
        st.error(f"Error: {str(e)}")
