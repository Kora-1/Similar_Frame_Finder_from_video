import streamlit as st
import requests
from PIL import Image
import io

API_URL = "http://localhost:8000"

st.title("Video Frame Similarity Search")

# --- Upload Video Section ---
st.header("1. Upload and Process a Video")
uploaded_video = st.file_uploader("Upload MP4 Video", type=["mp4"])
interval = st.number_input("Frame Extraction Interval (seconds)", min_value=1, max_value=10, value=1)

if uploaded_video and st.button("Upload and Extract Frames"):
    with st.spinner("Uploading and processing..."):
        files = {"file": (uploaded_video.name, uploaded_video, "video/mp4")}
        data = {"interval": str(interval)}
        response = requests.post(f"{API_URL}/upload-video/", files=files, data=data)
        if response.ok:
            st.success(response.json().get("message"))
        else:
            st.error(f"Error: {response.text}")

# --- Similarity Search Section ---
st.header("2. Upload an Image for Similarity Search")
uploaded_image = st.file_uploader("Upload Image for Similarity Search", type=["jpg", "jpeg", "png"])

top_k = st.slider("Number of Similar Frames to Show", 1, 10, 5)

if uploaded_image and st.button("Find Similar Frames"):
    with st.spinner("Searching..."):
        files = {"file": (uploaded_image.name, uploaded_image, "image/jpeg")}
        data = {"top_k": str(top_k)}
        response = requests.post(f"{API_URL}/find-similar/", files=files, data=data)
        if response.ok:
            results = response.json()['results']
            st.subheader("Top Similar Frames:")
            for res in results:
                frame_path = res['image_path']
                score = res['score']
                vector_preview = str(res['vector'][:10]) + "..."  # Shorten for display
                # Get the frame image from FastAPI server
                img_resp = requests.get(f"{API_URL}/get-frame/", params={"path": frame_path})
                if img_resp.ok:
                    img = Image.open(io.BytesIO(img_resp.content))
                    st.image(img, caption=f"Score: {score:.3f}\nVector: {vector_preview}", width=256)
                else:
                    st.write(f"Could not fetch image at {frame_path}")
        else:
            st.error(f"Error: {response.text}")
