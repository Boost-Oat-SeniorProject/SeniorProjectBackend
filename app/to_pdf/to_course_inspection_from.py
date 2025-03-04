import pdfplumber
from io import BytesIO
from database.database import SessionLocal
from fastapi.responses import JSONResponse

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def to_pdf(text):
    buffer = BytesIO()
    c = canvas.Canvas(buffer)

    for line in text:
        c.drawString(100, 750, line)
        c.drawString(100, 730, line)

    c.showPage()
    c.save()

    buffer.seek(0)  # Reset buffer position to the beginning
    return buffer


def test():
    table_format = [
        ["รหัสวิชา", "ชื่อรายวิชา(ภาษาอังกฤษ)", "หน่วยกิต", "ภาค/ปีการศึกษา", "เกรด"],
    ]

    pdf_path = "./to_pdf/CourseInspectionForm2560.pdf"
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()

    text = text.splitlines()
    # for line in text:
    #     print(line)


    return to_pdf(text)