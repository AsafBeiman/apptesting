import streamlit as st
from stlviewspart import STLViewer
from selenium_utils import run_automation
import tempfile
from PIL import Image
import io
import zipfile
import os

def crop_image_bytes(image_bytes, side_percent=10, top_percent=15):
    """Crop image with different percentages from sides and top/bottom"""
    image = Image.open(io.BytesIO(image_bytes))
    
    width, height = image.size
    crop_x = int(width * (side_percent / 100))
    crop_y = int(height * (top_percent / 100))
    
    cropped_image = image.crop((
        crop_x,           # left
        crop_y,          # top
        width - crop_x,  # right
        height - crop_y  # bottom
    ))
    
    output_buffer = io.BytesIO()
    cropped_image.save(output_buffer, format='PNG')
    return output_buffer.getvalue()

def init_session_state():
    if 'stl_viewer' not in st.session_state:
        st.session_state.stl_viewer = STLViewer()
    if 'captured_views' not in st.session_state:
        st.session_state.captured_views = []
    if 'style_paths' not in st.session_state:
        st.session_state.style_paths = []
    if 'azimuth' not in st.session_state:
        st.session_state.azimuth = 45
    if 'elevation' not in st.session_state:
        st.session_state.elevation = 45
    if 'generated_results' not in st.session_state:
        st.session_state.generated_results = []

def add_generated_result(view_path, style_path, strength, result_image):
    result_id = len(st.session_state.generated_results)
    # Crop the result image
    cropped_result = crop_image_bytes(result_image, side_percent=20, top_percent=5)
    
    result = {
        'id': result_id,
        'view_path': view_path,
        'style_path': style_path,
        'strength': strength,
        'result_image': cropped_result
    }
    st.session_state.generated_results.append(result)
    return result_id

def render_generated_results():
    if st.session_state.generated_results:
        st.subheader("Generated Images")
        
        # Display headers only once
        header_cols = st.columns([0.5, 0.8, 0.8, 2, 0.5])
        with header_cols[0]:
            st.subheader("Strength")
        with header_cols[1]:
            st.subheader("STL View")
        with header_cols[2]:
            st.subheader("Styling Reference")
        with header_cols[3]:
            st.subheader("Rendered Result")
        with header_cols[4]:
            st.subheader("Download")
        
        # Display content rows
        for result in st.session_state.generated_results:
            cols = st.columns([0.5, 0.8, 0.8, 2, 0.5])
            
            with cols[0]:
                st.write(f"{result['strength']}%")
            
            with cols[1]:
                st.image(result['view_path'])
            
            with cols[2]:
                st.image(result['style_path'])
            
            with cols[3]:
                st.image(result['result_image'])
            
            with cols[4]:
                st.download_button(
                    "Download Result",
                    result['result_image'],
                    f"vizcom_result_{result['id']}.png",
                    "image/png",
                    key=f"download_{result['id']}"
                )
        
        if len(st.session_state.generated_results) > 1:
            create_download_all_button()


def update_preview():
   if st.session_state.stl_viewer.plotter:
       preview = st.session_state.stl_viewer.get_view_image(
           st.session_state.azimuth,
           st.session_state.elevation
       )
       if preview is not None:
           # Convert to PIL Image and resize to fit container
           img = Image.fromarray(preview)
           container_height = 355
           aspect_ratio = img.width / img.height
           new_width = int(container_height * aspect_ratio)
           img = img.resize((new_width, container_height), Image.Resampling.LANCZOS)
           return img
   return None


def capture_view():
    if len(st.session_state.captured_views) < 3:
        new_view = st.session_state.stl_viewer.get_view_image(
            st.session_state.azimuth,
            st.session_state.elevation
        )
        if new_view is not None:
            # Convert to bytes
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                Image.fromarray(new_view).save(tmp_file.name)
                st.session_state.captured_views.append(tmp_file.name)
            return True
    return False


def render_stl_section(col1):
    with col1:
        st.subheader("STL Views Extraction")
        stl_file = st.file_uploader("Upload STL file", type=['stl'])

        if stl_file and st.session_state.stl_viewer.plotter is None:
            st.session_state.stl_viewer.initialize_mesh(stl_file)

        st.session_state.preset_views = st.selectbox(
            "Preset views",
            list(STLViewer.PRESET_VIEWS.keys()),
            index=5
        )

        preset = STLViewer.PRESET_VIEWS[st.session_state.preset_views]
        st.session_state.azimuth = st.slider("Azimuth", -180, 180, preset['azimuth'])
        st.session_state.elevation = st.slider("Elevation", -90, 90, preset['elevation'])

        preview_image = update_preview()
        if preview_image is not None:
            with st.container(height=355):
                st.image(preview_image)
        else:
            st.container().markdown(
                f"""
                <div style='height: 355px;
                            border: 1px solid #ccc;
                            display: flex;
                            align-items: center;
                            justify-content: center'>
                    STL preview
                </div>
                """,
                unsafe_allow_html=True
            )

        can_capture = len(st.session_state.captured_views) < 3
        if st.button("Capture view (up to 3)", disabled=not can_capture):
            capture_view()


def render_styling_section(col2):
    with col2:
        st.subheader("Styling References")
        uploaded_files = st.file_uploader(
            "Upload up to 4 styling image references",
            type=['png', 'jpg', 'jpeg'],
            accept_multiple_files=True
        )

        st.session_state.style_paths = []
        if uploaded_files:
            col2_1, col2_2 = st.columns(2)
            for idx, image in enumerate(uploaded_files[:4]):
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                    tmp_file.write(image.getvalue())
                    st.session_state.style_paths.append(tmp_file.name)
                with col2_1 if idx % 2 == 0 else col2_2:
                    with st.container(height=215):
                        st.image(image)
        return st.session_state.style_paths


def render_generated_views(col3):
    with col3:
        st.subheader("Model Generated Views")
        view_cols = st.columns(3)
        for i, col in enumerate(view_cols):
            with col:
                with st.container(height=150):
                    if i < len(st.session_state.captured_views):
                        st.image(st.session_state.captured_views[i], use_container_width=True)
                    else:
                        st.write(f'view{i + 1}')

def main():
    st.set_page_config(layout="wide")
    st.title("Vizcom AI Automation - STL Styling")
    init_session_state()

    col1, col2 = st.columns([1, 1])
    render_stl_section(col1)
    uploaded_files = render_styling_section(col2)

    col3, col4, col5 = st.columns([1.5, 0.7, 0.7])
    render_generated_views(col3)

    with col4:
        st.subheader("Rendering Info")
        prompt = st.text_input("Rendering prompt")
        selected_strengths = st.multiselect(
            "Styling Reference Strengths (up to 3)",
            ["95", "90", "85", "80", "75", "70", "65", "60", "55", "50"]
        )[:3]

    with col5:
        st.subheader("Vizcom Credentials")
        username = st.text_input("Username (email)")
        password = st.text_input("Password", type="password")

    if st.button("Run Automation"):
        if not (st.session_state.captured_views and uploaded_files and selected_strengths):
            st.error("Missing required inputs")
            return

        if not (username and password and prompt):
            st.error("Missing credentials or prompt")
            return

        for view in st.session_state.captured_views:
            for style in uploaded_files:
                for strength in selected_strengths:
                    progress_bar = st.progress(0)
                    result = run_automation(
                        view,
                        style,
                        prompt,
                        strength,
                        username,
                        password,
                        progress_bar
                    )
            
                    if result:
                        result_id = add_generated_result(view, style, strength, result)
                        st.success(f"Image {result_id + 1} generated successfully!")
    
    # Always render results section if there are any results
    if st.session_state.generated_results:
        st.markdown("---")  # Add a separator
        render_generated_results()


if __name__ == "__main__":
    main()
