import streamlit as st
import pyvista as pv
import tempfile
import os
from pathlib import Path
from stpyvista import stpyvista
import base64
import io
from PIL import Image

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

def capture_current_view(mesh, plotter, background_color, body_color):
    """Capture the current view using an off-screen plotter"""
    # Create off-screen plotter with same properties
    temp_plotter = pv.Plotter(off_screen=True, window_size=[400, 400])
    temp_plotter.background_color = background_color
    
    # Add mesh with same properties
    edges = mesh.extract_feature_edges(
        boundary_edges=False,
        non_manifold_edges=False,
        feature_angle=45,
        manifold_edges=False,
    )
    temp_plotter.add_mesh(
        mesh,
        color=body_color,
        smooth_shading=True,
        split_sharp_edges=True,
        edge_color='black'
    )
    temp_plotter.add_mesh(edges, color='black', line_width=2)
    
    # Copy camera position from interactive plotter
    temp_plotter.camera = plotter.camera
    
    # Render and get image
    temp_plotter.show(auto_close=False)
    image_array = temp_plotter.screenshot()
    temp_plotter.close()
    
    # Convert to PIL Image
    image = Image.fromarray(image_array)
    
    # Save to buffer
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    encoded_string = base64.b64encode(buffer.getvalue()).decode()
    
    return encoded_string

def main():
    st.title("STL Viewer with View Capture")

    # Initialize session state
    if 'mesh' not in st.session_state:
        st.session_state.mesh = None
    if 'captured_views' not in st.session_state:
        st.session_state.captured_views = []

    # Sidebar controls
    st.sidebar.header("Settings")
    background_color = "#e6e9ed"
    body_color = "#b5bec9"

    # File uploader
    uploaded_file = st.file_uploader("Upload STL file", type=['stl'])

    if uploaded_file:
        # Save file temporarily
        file_path = save_uploaded_file(uploaded_file)
        
        try:
            # Read STL file
            mesh = pv.read(file_path)
            
            # Create interactive plotter
            plotter = pv.Plotter(window_size=[400, 400])
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
            
            # Create columns for layout
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Interactive viewer
                stpyvista(plotter, key="stl_viewer")
            
            with col2:
                # Capture button
                if st.button("Capture Current View"):
                    img_data = capture_current_view(mesh, plotter, background_color, body_color)
                    st.session_state.captured_views.append(img_data)
                    st.success("View captured!")

            # Display captured views
            if st.session_state.captured_views:
                st.header("Captured Views")
                view_cols = st.columns(3)
                for idx, img_data in enumerate(st.session_state.captured_views):
                    col_idx = idx % 3
                    with view_cols[col_idx]:
                        st.image(f"data:image/png;base64,{img_data}")
                        download_btn = f"""
                        <a href="data:image/png;base64,{img_data}" 
                           download="view_{idx}.png">
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
