import os
from typing import List
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse
import cv2
import numpy as np
from pymongo import MongoClient
from bson.objectid import ObjectId

# -- Configuration --
OUTPUT_DIR = "frames"
MONGO_URI = "mongodb+srv://<username>:<password>@cluster0.decjvw7.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"   # Or use Atlas URI

os.makedirs(OUTPUT_DIR, exist_ok=True)
client = MongoClient(MONGO_URI)
db = client["video_db"]
frames_collection = db["frames"]

app = FastAPI()


# --- Functions ---
def extract_frames(video_path: str, interval_sec: int = 1, output_dir: str = OUTPUT_DIR) -> List[str]:
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    frame_interval = int(fps * interval_sec)
    saved_paths = []
    frame_count, saved_idx = 0, 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_count % frame_interval == 0:
            frame_fn = os.path.join(output_dir, f"{os.path.basename(video_path)}_frame_{saved_idx}.jpg")
            cv2.imwrite(frame_fn, frame)
            saved_paths.append(frame_fn)
            saved_idx += 1
        frame_count += 1
    cap.release()
    return saved_paths

def compute_feature_vector(image_path: str) -> np.ndarray:
    img = cv2.imread(image_path)
    img = cv2.resize(img, (128, 128))
    hist = cv2.calcHist([img], [0, 1, 2], None, [8,8,4], [0,256,0,256,0,256])
    hist = cv2.normalize(hist, hist).flatten()
    if hist.shape[0] != 256:
        hist = np.pad(hist, (0, 256-hist.shape[0]), mode='constant')
    return hist.astype(float)

def cosine_similarity(vec1, vec2):
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0:
        return 0
    return float(np.dot(vec1, vec2) / (norm1 * norm2))

# --- Endpoints ---
@app.post("/upload-video/")
async def upload_video(file: UploadFile = File(...), interval: int = Form(1)):
    video_path = f"temp_{file.filename}"
    with open(video_path, "wb") as f:
        f.write(await file.read())
    frame_paths = extract_frames(video_path, interval)
    for frame_path in frame_paths:
        feature_vec = compute_feature_vector(frame_path)
        frames_collection.insert_one({
            "image_path": frame_path,
            "vector": feature_vec.tolist()
        })
    os.remove(video_path)
    return {"message": f"Extracted and stored {len(frame_paths)} frames."}

@app.post("/find-similar/")
async def find_similar(file: UploadFile = File(...), top_k: int = Form(5)):
    query_path = "temp_query.jpg"
    with open(query_path, "wb") as f:
        f.write(await file.read())
    query_vec = compute_feature_vector(query_path)
    docs = list(frames_collection.find({}, {"image_path": 1, "vector": 1}))
    scored = []
    for doc in docs:
        sim = cosine_similarity(query_vec, np.array(doc["vector"]))
        scored.append({"image_path": doc["image_path"], "score": sim, "vector": doc["vector"]})
    top = sorted(scored, key=lambda x: -x["score"])[:top_k]
    os.remove(query_path)
    return JSONResponse(content={"results": top})

@app.get("/get-frame/")
async def get_frame(path: str):
    return FileResponse(path)
