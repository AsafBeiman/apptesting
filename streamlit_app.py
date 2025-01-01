import streamlit as st
from stlviewspart import STLViewer
from selenium_utils import run_automation
import tempfile
from PIL import Image

def init_session_state():
    if 'stl_viewer' not in st.session_state:
        st.session_state.stl_viewer = STLViewer()
    if 'captured_views' not in st.session_state:
        st.session_state.captured_views = []
    if 'azimuth' not in st.session_state:
        st.session_state.azimuth = 45
    if 'elevation' not in st.session_state:
        st.session_state.elevation = 45


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
        if preview_image is not None and preview_image.size > 0:
            with st.container(height=355):
                if st.session_state.stl_viewer.plotter is not None:
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

       if len(uploaded_files) > 4:
           st.warning("Maximum 4 images allowed. Only first 4 will be used.")

       if uploaded_files:
           col2_1, col2_2 = st.columns(2)
           for idx, image in enumerate(uploaded_files[:4]):
               with col2_1 if idx % 2 == 0 else col2_2:
                   with st.container(height=215):
                       # Save uploaded file to temp path
                       with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                           tmp_file.write(image.getvalue())
                           st.session_state.setdefault('style_paths', []).append(tmp_file.name)
                           st.image(image)
       return st.session_state.get('style_paths', [])


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

        progress_bar = st.progress(0)
        result = run_automation(
            st.session_state.captured_views[0],  # Now passing file path
            uploaded_files[0],
            prompt,
            selected_strengths[0],
            username,
            password,
            progress_bar
        )

        if result:
            st.success("Image generated successfully!")
            st.image(result)
            st.download_button(
                "Download Result",
                result,
                "vizcom_result.png",
                "image/png"
            )


if __name__ == "__main__":
    main()
