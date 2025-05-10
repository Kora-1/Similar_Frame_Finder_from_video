# Video Frame Similarity Search (FastAPI + Streamlit + MongoDB)

This project lets you upload videos, extract frames, represent them as feature vectors (color histograms), and search for similar frames using a simple image upload.

- **Backend:** FastAPI (handles video, feature extraction, MongoDB storage, and similarity search)
- **Frontend:** Streamlit (user-friendly interface for uploads and search)
- **Database:** MongoDB Atlas (recommended) or local MongoDB server

---

## Quick Start

### 1. **Clone the Repository**

```bash
git clone https://github.com/Kora-1/Similar_Frame_Finder_from_video
cd Similar_Frame_Finder_from_video
```

### 2. **Install Dependencies**

```bash
pip install fastapi uvicorn opencv-python numpy pymongo python-multipart streamlit requests pillow
```

### 3. **Set up MongoDB Atlas**

1. [Sign up for MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register) (free tier is enough).
2. Create a cluster, add a database, and create a database user.
3. Whitelist your IP address in “Network Access.”
4. Copy your cluster’s connection string, e.g.:
    ```
    mongodb+srv://:@cluster0.abcde.mongodb.net/?retryWrites=true&w=majority
    ```

### 4. **Configure MongoDB Connection**

- **Open `api.py`.**
- Find the following line at the top:
  ```python
  MONGO_URI = "mongodb+srv://<username>:<password>@cluster0.decjvw7.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
  ```
- **Replace it** with your own Atlas URI. It’s best to use environment variables for secrets in production.

### 5. **Start the FastAPI Backend**

```bash
uvicorn api:app --reload
```

FastAPI will now listen on `http://localhost:8000`.

### 6. **Start the Streamlit Frontend**

```bash
streamlit run streamlit.py
```

Streamlit will open at [http://localhost:8501](http://localhost:8501).

---

## Usage

1. **Upload an MP4 video** and set frame extraction interval to ingest video frames into the database.
2. **Upload an image** (a frame or any image) on the next section to search for the most visually similar frames using cosine similarity.
3. **View results:** Similar frames will be shown with their similarity score and preview.

---

## File Structure

```
api.py               # FastAPI backend
streamlit.py         # Streamlit user interface
frames/              # Directory to store extracted frames
README.md            # You are here!
```

---

## Configuration

- Edit the `MONGO_URI` at the top of `api.py` to use your own Atlas connection string.
- The `frames/` folder will be created to store extracted frame images.

---

## Notes

- For local development you can use a local MongoDB server as well.  
- For large-scale or production, consider MongoDB Atlas Vector Search for much faster embedding similarity queries.
- The similarity search in this template is done in Python, which is fine for hundreds or low-thousand images.

---

