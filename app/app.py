import fastapi
from fastapi import UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from database.database import init_db
from database.seeder import seed
import extraction_v1_1_0
import extraction_v1_2_0
from to_categories import to_categories

from to_pdf.to_course_inspection_from import test

@asynccontextmanager
async def lifespan(app):
    init_db()
    seed()
    yield


app = fastapi.FastAPI(lifespan=lifespan)

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
    if not file.filename.lower().endswith(".pdf"):
        return JSONResponse(
            status_code=400,
            content={"error": "Only PDF files are allowed."}
        )

    pdf_info = extraction_v1_1_0.extract_subjects(file.file)
    if not isinstance(pdf_info, JSONResponse):
        categories = to_categories(pdf_info)
        return categories
    return pdf_info

@app.post('/extract_v1_2')
async def extract(file : UploadFile):
    if not file.filename.lower().endswith(".pdf"):
        return JSONResponse(
            status_code=400,
            content={"error": "Only PDF files are allowed."}
        )

    pdf_info = extraction_v1_2_0.extract(file.file)

    return pdf_info