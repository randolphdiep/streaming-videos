from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi import FastAPI, UploadFile, File,Response
from starlette.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import mimetypes
from datetime import datetime

app = FastAPI()

origins = [
    "http://localhost:8000",  # Allow only this origin
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    # Generate a unique ID for the file based on the current datetime
    file_id = datetime.now().strftime("%Y%m%d%H%M%S")
    _, ext = os.path.splitext(file.filename)

    file_name = f"{file_id}{ext}"
    # Define the path for the video
    video_path = f"./uploaded-videos/{file_name}"

    # Save the video file
    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Append the original filename to a shared txt file
    with open("file-names.txt", "a") as log_file:
        log_file.write(f"{file_name}\n")
    
    # Return a success response
    return JSONResponse(content={"message": "Video uploaded successfully"}, status_code=200)

@app.get("/stream-video/{file_id}")
async def stream_video(file_id: str):
    log_file_path = "file-names.txt"
    video_directory = "./uploaded-videos/"
    try:
        with open(log_file_path, "r") as log_file:
            for line in log_file:
                current_file = line.split(".")
                current_file_name = current_file[0]
                if current_file_name == file_id:
                    video_path = os.path.join(video_directory, line).strip()
                    if os.path.exists(video_path):
                        mime_type, _ = mimetypes.guess_type(line.strip())
                        file_like = open(video_path, mode="rb")
                        return StreamingResponse(file_like, media_type=mime_type)
        raise HTTPException(status_code=404, detail="File ID not found in log")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Log file not found")
    except Exception as e:
        return Response(status_code=500, content=str(e))
    
@app.get("/files")
async def list_files():
    log_file_path = "file-names.txt"
    files_list = []
    try:
        with open(log_file_path, "r") as file:
            for line in file:
                clean_line = line.strip()
                if clean_line:
                    files_list.append(clean_line)
    except FileNotFoundError:
        return JSONResponse(content={"error": "Log file not found"}, status_code=404)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    return JSONResponse(files_list)