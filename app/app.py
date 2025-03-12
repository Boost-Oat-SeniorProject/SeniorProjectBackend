import fastapi
from fastapi import UploadFile
from fastapi.params import Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from contextlib import asynccontextmanager
import urllib.parse

from database.database import init_db
from database.seeder import seed
import extraction_v1_1_0
from to_categories import to_categories

from to_pdf.to_course_inspection_from import to_pdf

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

@app.post('/to_pdf')
def fill_pdf(results = Body(...)):
    encoded_filename = urllib.parse.quote("แบบตรวจสอบหลักสูตร.pdf")  # Encode for non-ASCII characters

    pdf_data = to_pdf(results)

    return StreamingResponse(
        pdf_data,  # Pass BytesIO buffer
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{encoded_filename}"'}
    )
    