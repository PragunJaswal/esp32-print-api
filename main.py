from fastapi import FastAPI, File, UploadFile, Request, Form
from fastapi.responses import FileResponse ,JSONResponse ,HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from PIL import Image
import os
from random import randint
import uuid
import datetime
import io



IMAGEDIR = "images/"
 
app = FastAPI()
@app.get("/")
def root():
    return{"Server is running"}
 
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
 

# Define the dimensions of A4 paper in pixels (assuming 72 dpi)
A4_WIDTH = 595
A4_HEIGHT = 842

@app.get('/file-upload', response_class=HTMLResponse)
def get_basic_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

@app.post('/file-upload', response_class=HTMLResponse)
async def post_basic_form(request: Request, file: UploadFile = File(...)):
    print(f'Filename: {file.filename}')

    contents = await file.read()

    # Open the image using PIL
    image = Image.open(io.BytesIO(contents))

    # Convert the image to RGB if it's in RGBA format
    if image.mode == 'RGBA':
        image = image.convert('RGB')

    # Calculate the aspect ratios
    image_aspect_ratio = image.width / image.height
    a4_aspect_ratio = A4_WIDTH / A4_HEIGHT

    # Crop and resize the image
    if image_aspect_ratio > a4_aspect_ratio:
        new_width = int(image.height * a4_aspect_ratio)
        image = image.crop(((image.width - new_width) // 2, 0, (image.width + new_width) // 2, image.height))
    else:
        new_height = int(image.width / a4_aspect_ratio)
        image = image.crop((0, (image.height - new_height) // 2, image.width, (image.height + new_height) // 2))
    image = image.resize((A4_WIDTH, A4_HEIGHT))

    # Convert the image back to bytes
    output = io.BytesIO()
    image.save(output, format="JPEG")
    cropped_contents = output.getvalue()

    # Save the cropped file
    with open(f"{IMAGEDIR}{file.filename}", "wb") as f:
        f.write(cropped_contents)

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
    print(path)
    # img=Image.open(path)
    # img_crop= img.crop(box= (20,20,200,200))
    # img_crop.save("images/img.png")

    # Delete all other files except the latest one
    for file in files[1:]:
        file_path = os.path.join(IMAGEDIR, file)
        os.remove(file_path)

    return FileResponse(path)
