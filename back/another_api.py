from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi import Request, Response, Form, Depends, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse,JSONResponse
from fastapi import Header
from fastapi.templating import Jinja2Templates
import shutil
import os
from datetime import datetime


app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
CHUNK_SIZE = 1024*1024
video_path = Path("./uploaded-videos/20240414124036.mp4")


@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", context={"request": request})


@app.get("/video")
async def video_endpoint(range: str = Header(None)):
    start, end = range.replace("bytes=", "").split("-")
    start = int(start)
    end = int(end) if end else start + CHUNK_SIZE
    with open(video_path, "rb") as video:
        video.seek(start)
        data = video.read(end - start)
        filesize = str(video_path.stat().st_size)
        headers = {
            'Content-Range': f'bytes {str(start)}-{str(end)}/{filesize}',
            'Accept-Ranges': 'bytes'
        }
        return Response(data, status_code=206, headers=headers, media_type="video/mp4")
    
@app.get('/upload-video', response_class=HTMLResponse)
def get_basic_form(request: Request):
    return templates.TemplateResponse("basic-form.html", {"request": request})

@app.post("/upload-video")
async def upload_video(title: str = Form(...), file: UploadFile = File(...), image: UploadFile = File(...)):
    # Generate a unique ID for the file based on the current datetime
    file_id = datetime.now().strftime("%Y%m%d%H%M%S")
    _, ext = os.path.splitext(file.filename)

    print(title)

     # Check if the file is a video
    if ext not in ['.mp4', '.avi', '.mov', '.flv', '.wmv']:  # Add or remove extensions as needed
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a video file.")

    file_name = f"{file_id}{ext}"
    # Define the path for the video
    video_path = f"./uploaded-videos/{file_name}"

    # Save the video file
    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Append the original filename to a shared txt file
    with open("file-names.txt", "a") as log_file:
        log_file.write(f"{file_name}\n")

    # Save the image file
    _, image_ext = os.path.splitext(image.filename)
    image_name = f"{file_id}{image_ext}"
    image_path = f"./uploaded-images/{image_name}"
    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    
    # Return a success response
    return JSONResponse(content={"message": "Video uploaded successfully"}, status_code=200)