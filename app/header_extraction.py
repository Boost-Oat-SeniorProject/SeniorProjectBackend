import pytesseract
import cv2
import numpy as np
from pdf2image import convert_from_bytes
import re
from fastapi import HTTPException

def detect_tables(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV)
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
    horizontal_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
    vertical_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
    table_mask = cv2.add(horizontal_lines, vertical_lines)

    contours, _ = cv2.findContours(table_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:1]
    table_bbox = cv2.boundingRect(contours[0])
    return table_bbox

def extract_from_table(image, table_bbox, table_mask, table_pos):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    x, y, w, h = table_bbox

    # take out table grid lines
    for yi in range(gray_image.shape[0]):
        for xi in range(gray_image.shape[1]):
            if table_mask[yi][xi]  > 40:
                gray_image[yi][xi] = 255

    # extract to text
    text = ""
    for i in range(len(table_pos) - 1):
        cropped_table = gray_image[y:y+h, table_pos[i][0]:table_pos[i + 1][0]]

        text += pytesseract.image_to_string(cropped_table, lang="eng", config="--psm 6")
    return text

def extract_from_image(image, table_bbox):
    x, y, w, h = table_bbox
    detail = image[:y, :x+w]
    text = pytesseract.image_to_string(detail, lang="tha+eng", config="--psm 6")
    return text

def remove_special_character(text):
    text = text.replace('(', '')
    text = text.replace(')', '')
    text = text.replace('|', '')
    return text


def extract(pdf):
    try:
        # Read the file content into memory
        pdf_bytes = pdf.read()
        # Convert the PDF bytes to images
        images = convert_from_bytes(pdf_bytes, dpi=300)

        # Process each page
        for i, image in enumerate(images):
            # image_path = f"page_{i+1}.png"
            # image.save(image_path, "PNG")
            image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            table_bbox = detect_tables(image)

            text = ""
            text = extract_from_image(image, table_bbox)
            # text  += extract_from_table(image, table_bbox, table_mask, table_pos)

            text = remove_special_character(text)

            student_id = re.search('Student.+No.+[0-9]{10}', text)
            if student_id is None:
                student_id = ''
            else:
                student_id = student_id.group()[-10:]

            # extract student's Thai name
            student_thai_name = re.search(r'((นาย|นาง|นางสาว) *([\u0E00-\u0E7F]+ )+)', text)
            if student_thai_name is None:
                student_thai_name = ''
            else:
                student_thai_name = student_thai_name.group()
                words = student_thai_name.split(' ')
                words.remove('')
                if len(words) > 2:
                    student_thai_name = f"{words[0]}{words[1]} {words[2]}"

            return student_id, student_thai_name
            



    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {str(e)}"
        )

