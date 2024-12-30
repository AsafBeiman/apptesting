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

    # Initialize session state for colors
    if 'background_color' not in st.session_state:
        st.session_state.background_color = "#e6e9ed"
    if 'body_color' not in st.session_state:
        st.session_state.body_color = "#b5bec9"
    if 'generated_views' not in st.session_state:
        st.session_state.generated_views = {}

    # Sidebar controls
    st.sidebar.header("Settings")
    background_color = st.sidebar.color_picker("Background Color", st.session_state.background_color)
    body_color = st.sidebar.color_picker("Body Color", st.session_state.body_color)

    # Update colors if changed
    if background_color != st.session_state.background_color or body_color != st.session_state.body_color:
        st.session_state.background_color = background_color
        st.session_state.body_color = body_color
        st.session_state.generated_views = {}  # Clear cached views
        st.rerun()

    # File uploader
    uploaded_file = st.file_uploader("Upload STL file", type=['stl'])

    if uploaded_file:
        # Save file temporarily
        file_path = save_uploaded_file(uploaded_file)
        
        try:
            # Read STL file
            mesh = pv.read(file_path)
            
            # Generate button
            if st.button("Generate All Views"):
                # Progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Generate all views
                for idx, (view_name, angles) in enumerate(PRESET_VIEWS.items()):
                    status_text.text(f"Generating {view_name} view...")
                    
                    # Generate view
                    img_data = generate_view(
                        mesh=mesh,
                        background_color=background_color,
                        body_color=body_color,
                        azimuth=angles['azimuth'],
                        elevation=angles['elevation']
                    )
                    
                    # Store in session state
                    st.session_state.generated_views[view_name] = {
                        'data': img_data,
                        'timestamp': datetime.now().strftime("%Y%m%d_%H%M%S")
                    }
                    
                    # Update progress
                    progress_bar.progress((idx + 1) / len(PRESET_VIEWS))
                
                status_text.text("All views generated!")

            # Display generated views
            if st.session_state.generated_views:
                st.header("Generated Views")
                cols = st.columns(3)
                
                for idx, (view_name, view_data) in enumerate(st.session_state.generated_views.items()):
                    col_idx = idx % 3
                    with cols[col_idx]:
                        st.image(
                            f"data:image/png;base64,{view_data['data']}",
                            caption=view_name,
                            use_column_width=True
                        )
                        
                        # Download button
                        download_btn = f"""
                        <a href="data:image/png;base64,{view_data['data']}" 
                           download="{view_name}_{view_data['timestamp']}.png">
                            Download Image
                        </a>
                        """
                        st.markdown(download_btn, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error processing STL file: {str(e)}")
            
        finally:
            # Cleanup
            if os.path.exists(file_path):
                os.unlink(file_path)

if __name__ == "__main__":
    main()
