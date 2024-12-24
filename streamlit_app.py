import streamlit as st
from pathlib import Path

st.set_page_config(page_title="STL Uploader")

st.title("STL File Uploader")

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# File uploader
uploaded_file = st.file_uploader("Choose an STL file", type=['stl'])

if uploaded_file is not None:
    # Display file info
    file_details = {
        "Filename": uploaded_file.name,
        "File size": f"{uploaded_file.size / 1024:.2f} KB"
    }

    st.write("File Details:")
    for key, value in file_details.items():
        st.write(f"{key}: {value}")

    # Save the file
    if st.button("Save File"):
        file_path = UPLOAD_DIR / uploaded_file.name
        try:
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"File saved successfully at {file_path}")

            # Display the list of uploaded files
            st.write("\nFiles in upload directory:")
            files = list(UPLOAD_DIR.glob("*.stl"))
            for file in files:
                st.write(f"- {file.name} ({file.stat().st_size / 1024:.2f} KB)")

        except Exception as e:
            st.error(f"Error saving file: {str(e)}")
else:
    st.info("Please upload an STL file")

# Add basic information in the sidebar
with st.sidebar:
    st.header("About")
    st.write("""
    This simple app allows you to upload STL (STereoLithography) files.
    Files are saved in the 'uploads' directory.
    """)