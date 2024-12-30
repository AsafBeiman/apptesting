import streamlit as st
import pyvista as pv
import tempfile
import os
from pathlib import Path
import base64
from datetime import datetime
import numpy as np
from PIL import Image
import io
from stpyvista import stpyvista


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


def generate_view(mesh, background_color, body_color, azimuth, elevation):
    """Generate a single view of the mesh"""
    plotter = pv.Plotter(off_screen=True, window_size=[800, 600])
    plotter.background_color = background_color

    # Add mesh with edges
    edges = mesh.extract_feature_edges(
        boundary_edges=False,
        non_manifold_edges=False,
        feature_angle=45,
        manifold_edges=False,
    )
    plotter.add_mesh(mesh, color=body_color, smooth_shading=True,
                     split_sharp_edges=True, edge_color='black')
    plotter.add_mesh(edges, color='black', line_width=2)

    # Set camera position
    plotter.camera.position = (0, 0, 1)
    plotter.camera.up = (0, 1, 0)
    plotter.reset_camera()
    plotter.camera.azimuth = azimuth
    plotter.camera.elevation = elevation

    # Get image
    plotter.show(auto_close=False)
    image_array = plotter.image
    plotter.close()

    # Convert to base64
    image = Image.fromarray(image_array)
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    encoded_string = base64.b64encode(buffer.getvalue()).decode()

    return encoded_string


def main():
    st.title("STL Multi-View Generator")

    # Sidebar controls
    st.sidebar.header("Settings")
    background_color = "#e6e9ed" #st.sidebar.color_picker("Background Color", st.session_state.background_color)
    body_color = "#b5bec9" #st.sidebar.color_picker("Body Color", st.session_state.body_color)



    # File uploader
    uploaded_file = st.file_uploader("Upload STL file", type=['stl'])

    if uploaded_file:
        # Save file temporarily
        file_path = save_uploaded_file(uploaded_file)

        try:
            # Read STL file
            mesh = pv.read(file_path)
            # Generate button
            # Add mesh with edges
            edges = mesh.extract_feature_edges(
                boundary_edges=False,
                non_manifold_edges=False,
                feature_angle=45,
                manifold_edges=False,
            )
            plotter = pv.Plotter(window_size=[300, 300])
            plotter.add_mesh(mesh, color=body_color, smooth_shading=True,
                             split_sharp_edges=True, edge_color='black')
            plotter.add_mesh(edges, color='black', line_width=2)
            plotter.background_color = background_color
            stpyvista(plotter, key=f"sphere_1")
        except Exception as e:
            st.error(f"Error processing STL file: {str(e)}")

        finally:
            # Cleanup
            if os.path.exists(file_path):
                os.unlink(file_path)


if __name__ == "__main__":
    main()
