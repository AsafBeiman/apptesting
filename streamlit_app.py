import streamlit as st
import pyvista as pv
from stpyvista import stpyvista

res = st.slider("Resolution", 5, 100, 20, 5)

# Set up plotter
plotter = pv.Plotter(window_size=[300, 300])

# Create element
sphere = pv.Sphere(phi_resolution=res, theta_resolution=res)
plotter.add_mesh(sphere, name="sphere", show_edges=True)
plotter.view_isometric()

# Pass the plotter (not the mesh) to stpyvista
stpyvista(plotter, key=f"sphere_{res}")
