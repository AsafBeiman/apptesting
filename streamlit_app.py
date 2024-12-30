import streamlit as st
import pyvista as pv
import tempfile
import os
from pathlib import Path
from stpyvista import stpyvista

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

def main():
    st.title("STL Viewer")

    # Initialize session state for the mesh
    if 'mesh' not in st.session_state:
        st.session_state.mesh = None

    # Sidebar controls
    st.sidebar.header("Settings")
    background_color = "#e6e9ed"
    body_color = "#b5bec9"

    # File uploader
    uploaded_file = st.file_uploader("Upload STL file", type=['stl'])

    if uploaded_file:
        try:
            # Save file temporarily
            file_path = save_uploaded_file(uploaded_file)
            
            # Read STL file
            mesh = pv.read(file_path)

            # Create plotter
            plotter = pv.Plotter(window_size=[800, 600])
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

            # Set up the camera
            plotter.reset_camera()
            plotter.camera_position = 'iso'
            
            # Display the plotter
            stpyvista(plotter, key="stl_viewer")

            # Cleanup
            os.unlink(file_path)

        except Exception as e:
            st.error(f"Error processing STL file: {str(e)}")

if __name__ == "__main__":
    main()
