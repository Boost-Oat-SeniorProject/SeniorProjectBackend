import fastapi
from fastapi import UploadFile
from fastapi.middleware.cors import CORSMiddleware
from database.database import engine
from extract_v1_0_0 import *

app = fastapi.FastAPI()


origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get('/')
def index():    
    return 'hi'

@app.post('/extract')
async def extract(file : UploadFile):
    text = pdf_to_text_first_page(file.file)

    name = extract_info(text)

    enrolled = extract_subjects(text)

    subjects = []
    for detail in enrolled:
        for enroll in detail['enroll']:
            subjects.append(enroll)

    return {'subjects' : subjects}