import pyvista as pv
import tempfile
import streamlit as st
from typing import Dict, List, Tuple

class STLViewer:
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

    def __init__(self):
        pv.start_xvfb()
        self.plotter = None
        self.mesh_path = None

    def setup_plotter(self, mesh, background_color="#e6e9ed", body_color="#b5bec9"):
        plotter = pv.Plotter(off_screen=True, window_size=[600, 600])
        plotter.background_color = background_color
        edges = mesh.extract_feature_edges(boundary_edges=False, non_manifold_edges=False, feature_angle=45, manifold_edges=False)
        plotter.add_mesh(mesh, color=body_color, smooth_shading=True, split_sharp_edges=True, edge_color='black')
        plotter.add_mesh(edges, color='black', line_width=2)
        return plotter

    def save_uploaded_file(self, uploaded_file) -> str:
        if uploaded_file:
            tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.stl')
            tfile.write(uploaded_file.getvalue())
            return tfile.name
        return None

    def get_view_image(self, azimuth: float, elevation: float) -> bytes:
        if not self.plotter:
            return None
        self.plotter.reset_camera()
        self.plotter.camera_position = 'xy'
        self.plotter.camera.azimuth = azimuth
        self.plotter.camera.elevation = elevation
        self.plotter.show(auto_close=False)
        return self.plotter.screenshot()

    def initialize_mesh(self, stl_file) -> bool:
        try:
            self.mesh_path = self.save_uploaded_file(stl_file)
            mesh = pv.read(self.mesh_path)
            self.plotter = self.setup_plotter(mesh)
            return True
        except Exception as e:
            st.error(f"Error initializing mesh: {str(e)}")
            return False
