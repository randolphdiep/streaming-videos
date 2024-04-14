from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi import FastAPI, UploadFile, File,Response
from starlette.responses import StreamingResponse
import shutil
import os
from datetime import datetime

app = FastAPI()

@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    file_id = datetime.now().strftime("%Y%m%d%H%M%S")
    _, ext = os.path.splitext(file.filename)
    with open(f"./uploaded-videos/{file_id}{ext}", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return JSONResponse(content={"message": "Video uploaded successfully"}, status_code=200)

@app.get("/stream-video")
async def stream_video():
    try:
        video_path = "./uploaded-videos/20240414110816.mp4"
        file_like = open(video_path, mode="rb")
        response = StreamingResponse(file_like, media_type="video/mp4")
        return response
    except Exception as e:
        return Response(status_code=500, content=str(e))