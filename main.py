from fastapi import FastAPI, File, UploadFile, Request, Form
from fastapi.responses import FileResponse ,JSONResponse ,HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os
from random import randint
import uuid
import datetime



IMAGEDIR = "images/"
 
app = FastAPI()
@app.get("/")
def root():
    return{"Server is running"}
 
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
 
@app.get('/file-upload', response_class=HTMLResponse)
def get_basic_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})
 
@app.post('/file-upload', response_class=HTMLResponse)
async def post_basic_form(request: Request, file: UploadFile = File(...)):
    print(f'Filename: {file.filename}')
     
    contents = await file.read()
     
    #save the file
    with open(f"{IMAGEDIR}{file.filename}", "wb") as f:
        f.write(contents)
 
    return templates.TemplateResponse("form.html", {"request": request})
 
 
@app.get("/show/")
async def read_latest_file():
    files = os.listdir(IMAGEDIR)

    if not files:
        return JSONResponse(content={"message": "No images found"}, status_code=404)

    # Sort files based on modification timestamp (newest first)
    files.sort(key=lambda x: os.path.getmtime(os.path.join(IMAGEDIR, x)), reverse=True)

    latest_file = files[0]
    path = os.path.join(IMAGEDIR, latest_file)

    # Delete all other files except the latest one
    for file in files[1:]:
        file_path = os.path.join(IMAGEDIR, file)
        os.remove(file_path)

    return FileResponse(path)
