# import streamlit as st
# import pyvista as pv
# from stpyvista import stpyvista
# import tempfile
# import os
# from pathlib import Path
# import base64
# from datetime import datetime

# # Initialize PyVista and Streamlit settings
# pv.start_xvfb()
# st.set_page_config(layout="wide")

# # Define preset views
# PRESET_VIEWS = {
#     'Front': {'azimuth': 0, 'elevation': 0},
#     'Right': {'azimuth': 90, 'elevation': 0},
#     'Left': {'azimuth': -90, 'elevation': 0},
#     'Back': {'azimuth': 180, 'elevation': 0},
#     'Top': {'azimuth': 0, 'elevation': 90},
#     'Iso Right Front': {'azimuth': 45, 'elevation': 45},
#     'Iso Right Back': {'azimuth': 135, 'elevation': 45},
#     'Iso Left Front': {'azimuth': -45, 'elevation': 45},
#     'Iso Left Back': {'azimuth': -135, 'elevation': 45},
# }

# def save_uploaded_file(uploaded_file):
#     """Save uploaded file temporarily and return the path"""
#     if uploaded_file is not None:
#         tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.stl')
#         tfile.write(uploaded_file.getvalue())
#         return tfile.name
#     return None

# def capture_view(plotter):
#     """Capture current view and return base64 encoded image"""
#     import numpy as np
#     import io
#     from PIL import Image
#     plotter.show()
#     # Get image array directly from plotter
#     image_array = plotter.image

#     # Convert to PIL Image
#     image = Image.fromarray(image_array)
    
#     # Save to bytes buffer
#     buffer = io.BytesIO()
#     image.save(buffer, format='PNG')
    
#     # Get base64 encoded string
#     encoded_string = base64.b64encode(buffer.getvalue()).decode()
#     plotter.close()
#     return encoded_string

# def main():
#     st.title("STL Viewer and Capture")

#     # Initialize session state
#     if 'captured_images' not in st.session_state:
#         st.session_state.captured_images = []
        
#     # Use session state for plotter settings
#     if 'background_color' not in st.session_state:
#         st.session_state.background_color = "#e6e9ed"
#     if 'body_color' not in st.session_state:
#         st.session_state.body_color = "#b5bec9"

#     # File uploader
#     uploaded_file = st.file_uploader("Upload STL file", type=['stl'])

#     if uploaded_file:
#         # Save file temporarily
#         file_path = save_uploaded_file(uploaded_file)

#         # Sidebar controls
#         st.sidebar.header("View Settings")

#         # Color pickers with session state
#         new_background_color = st.sidebar.color_picker("Background Color", st.session_state.background_color)
#         new_body_color = st.sidebar.color_picker("Body Color", st.session_state.body_color)
        
#         # Update colors if changed
#         if new_background_color != st.session_state.background_color or new_body_color != st.session_state.body_color:
#             st.session_state.background_color = new_background_color
#             st.session_state.body_color = new_body_color
#             st.rerun()
            
#         # Read STL file
#         mesh = pv.read(file_path)

#         # Create plotter
#         plotter = pv.Plotter(window_size=[800, 600])
#         plotter.background_color = st.session_state.background_color
        
#         # Add mesh with edges
#         edges = mesh.extract_feature_edges(
#             boundary_edges=False,
#             non_manifold_edges=False,
#             feature_angle=45,
#             manifold_edges=False,
#         )
#         plotter.add_mesh(mesh, color=st.session_state.body_color, smooth_shading=True, 
#                         split_sharp_edges=True, edge_color='black')
#         plotter.add_mesh(edges, color='black', line_width=2)
#         plotter.reset_camera()
        
#         # Create columns for preset view buttons
#         st.subheader("Preset Views")
#         button_cols = st.columns(5)  # 5 buttons per row
            
#         for idx, (view_name, angles) in enumerate(PRESET_VIEWS.items()):
#             col_idx = idx % 5
#             with button_cols[col_idx]:
#                 if st.button(view_name):
#                     plotter.camera.azimuth = angles['azimuth']
#                     plotter.camera.elevation = angles['elevation']
#                     st.rerun()

#         # Create two columns for the viewer and capture button
#         col1, col2 = st.columns([4, 1])

#         with col1:
#             # Display the interactive viewer
#             stpyvista(plotter, key="stl_viewer")

#         with col2:
#             # Capture button
#             if st.button("Capture View"):
#                 img_data = capture_view(plotter)
#                 timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#                 st.session_state.captured_images.append({
#                     'data': img_data,
#                     'timestamp': timestamp
#                 })
#                 st.success("View captured!")

#         # Display captured images
#         if st.session_state.captured_images:
#             st.header("Captured Views")
#             cols = st.columns(3)
#             for idx, img in enumerate(st.session_state.captured_images):
#                 col_idx = idx % 3
#                 with cols[col_idx]:
#                     st.image(
#                         f"data:image/png;base64,{img['data']}",
#                         caption=f"View {img['timestamp']}",
#                         use_column_width=True
#                     )
#                     download_btn = f"""
#                     <a href="data:image/png;base64,{img['data']}" 
#                        download="view_{img['timestamp']}.png">
#                         Download Image
#                     </a>
#                     """
#                     st.markdown(download_btn, unsafe_allow_html=True)

#         # Cleanup
#         os.unlink(file_path)

# if __name__ == "__main__":
#     main()

import streamlit as st
from vedo import Mesh, Plotter
import os
import tempfile
from pathlib import Path

# Define preset views
VIEWS = {
    'front': {'azimuth': 0, 'elevation': 0},
    'right': {'azimuth': 90, 'elevation': 0},
    'left': {'azimuth': -90, 'elevation': 0},
    'back': {'azimuth': 180, 'elevation': 0},
    'top': {'azimuth': 0, 'elevation': 90},
    'iso_right_front_top': {'azimuth': 45, 'elevation': 45},
    'iso_right_back_top': {'azimuth': 135, 'elevation': 45},
    'iso_left_front_top': {'azimuth': -45, 'elevation': 45},
    'iso_left_back_top': {'azimuth': -135, 'elevation': 45},
}

def save_uploaded_file(uploaded_file):
    """Save uploaded file temporarily and return the path"""
    if uploaded_file is not None:
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.stl')
        tfile.write(uploaded_file.getvalue())
        return tfile.name
    return None

def visualize_stl(stl_file, output_dir, backround_color, body_color, view_name, azimuth, elevation):
    """Generate a single view of the STL file"""
    # Create output directory
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Load and setup mesh
    mesh = Mesh(stl_file)
    mesh.color(body_color)
    edges = mesh.boundaries(feature_angle=45)
    if edges:
        edges.color('black').lw(1)

    # Create plotter
    plt = Plotter(offscreen=True, axes=0)
    plt.background(backround_color)
    plt.add([mesh, edges])
    
    plt.show(interactive=False)
    plt.reset_camera()
    plt.camera.Azimuth(azimuth)
    plt.camera.Elevation(elevation)
    
    output_path = f"{output_dir}/{view_name}.jpeg"
    plt.screenshot(output_path)
    plt.close()
    
    return output_path

def main():
    st.title("STL Multi-View Generator")
    
    # Initialize session state for colors
    if 'background_color' not in st.session_state:
        st.session_state.background_color = "#e6e9ed"
    if 'body_color' not in st.session_state:
        st.session_state.body_color = "#b5bec9"
        
    # Sidebar controls
    st.sidebar.header("Settings")
    background_color = st.sidebar.color_picker("Background Color", st.session_state.background_color)
    body_color = st.sidebar.color_picker("Body Color", st.session_state.body_color)
    
    # File uploader
    uploaded_file = st.file_uploader("Upload STL file", type=['stl'])
    
    if uploaded_file:
        # Save file temporarily
        temp_stl_path = save_uploaded_file(uploaded_file)
        
        # Create temporary directory for outputs
        temp_output_dir = tempfile.mkdtemp()
        
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Generate all views
            image_paths = []
            for idx, (view_name, angles) in enumerate(VIEWS.items()):
                status_text.text(f"Generating {view_name} view...")
                image_path = visualize_stl(
                    stl_file=temp_stl_path,
                    output_dir=temp_output_dir,
                    backround_color=background_color,
                    body_color=body_color,
                    view_name=view_name,
                    azimuth=angles['azimuth'],
                    elevation=angles['elevation']
                )
                image_paths.append(image_path)
                progress_bar.progress((idx + 1) / len(VIEWS))
            
            # Display images in a grid
            status_text.text("All views generated!")
            st.header("Generated Views")
            
            # Create three columns
            cols = st.columns(3)
            
            # Display images in the columns
            for idx, image_path in enumerate(image_paths):
                col_idx = idx % 3
                with cols[col_idx]:
                    view_name = Path(image_path).stem
                    st.image(image_path, caption=view_name.title(), use_column_width=True)
                    
                    # Add download button for each image
                    with open(image_path, "rb") as file:
                        st.download_button(
                            label=f"Download {view_name}",
                            data=file,
                            file_name=f"{view_name}.jpeg",
                            mime="image/jpeg"
                        )
            
        except Exception as e:
            st.error(f"Error processing STL file: {str(e)}")
            
        finally:
            # Cleanup
            if os.path.exists(temp_stl_path):
                os.unlink(temp_stl_path)
            if os.path.exists(temp_output_dir):
                for file in os.listdir(temp_output_dir):
                    os.unlink(os.path.join(temp_output_dir, file))
                os.rmdir(temp_output_dir)

if __name__ == "__main__":
    main()
