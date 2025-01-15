import fastapi
from fastapi import UploadFile
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database.database import init_db
from database.seeder import seed
import extraction_v1_1_0

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
    pdf_info = extraction_v1_1_0.extract_subjects(file.file)

    return pdf_info