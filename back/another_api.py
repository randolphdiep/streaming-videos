from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi import Request, Response, Form, Depends, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse,RedirectResponse
from fastapi import Header
from fastapi.templating import Jinja2Templates
import shutil
import os
import json
from datetime import datetime


app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploaded-images", StaticFiles(directory="uploaded-images"), name="uploaded-images")
CHUNK_SIZE = 1024*1024
# video_path = Path("./uploaded-videos/20240414124036.mp4")


@app.get("/streaming/{file_id}")
async def read_root(request: Request, file_id: str):
    # Đọc dữ liệu từ file-info.json
    with open("file-info.json", "r") as log_file:
        data = json.load(log_file)

    # Tìm thông tin về video có file_id tương ứng
    video_info = next((video for video in data if video["file_id"] == file_id), None)
    if video_info is None:
        raise HTTPException(status_code=404, detail="Video not found")

    # Trả về template với thông tin về video và danh sách các video khác
    return templates.TemplateResponse("streaming-form.html",
                                      {"request": request, "file_id": file_id, "video_info": video_info, "video_list": data})



@app.get("/", response_class=HTMLResponse)
async def get_video_info(request: Request):
    with open("file-info.json", "r") as log_file:
        data = json.load(log_file)
        if isinstance(data, dict):  # Check if data is a dictionary
            data = [data]  # Convert data to a list containing one element
        return templates.TemplateResponse('list-video-form.html', {"request": request, "video_info": data})



@app.get("/video/{file_id}")
async def video_endpoint(range: str = Header(None), file_id: str = None):
    # read file file-info.json and find the file with the file_id and extract the extension
    with open("file-info.json", "r") as log_file:
        data = json.load(log_file)
    for item in data:
        if item["file_id"] == file_id:
            video_path = Path(f"./uploaded-videos/{file_id}{item['ext']}")
            break
    else:
        raise HTTPException(status_code=404, detail="File not found")
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
    return templates.TemplateResponse("upload-form.html", {"request": request})

@app.post("/upload-video")
async def upload_video(title: str = Form(...), file: UploadFile = File(...), image: UploadFile = File(...)):
    # Generate a unique ID for the file based on the current datetime
    file_id = datetime.now().strftime("%Y%m%d%H%M%S")
    _, ext = os.path.splitext(file.filename)

    data = {"file_id": file_id, "title": title, "ext": ext}
    # Read existing data
    with open("file-info.json", "r") as log_file:
        existing_data = json.load(log_file)

    # Append new data
    existing_data.append(data)

    with open("file-info.json", "w") as log_file:
        json.dump(existing_data, log_file)

     # Check if the file is a video
    if ext not in ['.mp4', '.avi', '.mov', '.flv', '.wmv']:  # Add or remove extensions as needed
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a video file.")

    file_name = f"{file_id}{ext}"
    # Define the path for the video
    video_path = f"./uploaded-videos/{file_name}"

    # Save the video file
    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Save the image file
    _, image_ext = os.path.splitext(image.filename)
    image_name = f"{file_id}{image_ext}"
    image_path = f"./uploaded-images/{image_name}"
    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    return RedirectResponse("/", status_code=303)

