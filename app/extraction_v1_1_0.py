import pdfplumber
import PyPDF2
import pandas as pd
import re

def extract_subjects(pdf):
    text = ""
    reader = PyPDF2.PdfReader(pdf)
    if len(reader.pages) > 0:
        page = reader.pages[0]
        text = page.extract_text()

    # extract student's id
    student_id = re.search('Student +No +[0-9]{10}', text)
    student_id = student_id.group()
    # print(student_id.group()[-10:])

    # extract student's name
    student_english_name = re.search('Name +([a-zA-Z]+ )+', text)
    student_english_name = student_english_name.group().split(' ')
    student_english_name = [x for x in student_english_name if x != '']
    student_english_name = [x for x in student_english_name[1:4]]
    student_english_name = ' '.join(student_english_name)
    # print(student_english_name)

    # extract student's Thai name
    student_thai_name = re.search(r'( *[\u0E00-\u0E7F]+ )+', text)
    student_thai_name = student_thai_name.group().replace(' ', '')
    print(student_thai_name)

    rows_array = []
    with pdfplumber.open(pdf) as pdf:
        first_page = pdf.pages[0]
        tables = first_page.extract_tables() 
        
        # extract subjects for table
        cleaned_tables = []
        for table in tables:
            df = pd.DataFrame(table)
            df.columns = df.iloc[0]  # Set the first row as column headers
            df = df[1:]  # Remove the header row
            cleaned_tables.append(df)

        df = pd.DataFrame(cleaned_tables[0])

        ## list columns of df
        # list(cleaned_tables[0].columns.values)
        df.columns = ['Course\nCode', 'Course Title', 'Grade', 'Credit', 
                    'Course\nCode.1', 'Course Title.1', 'Grade.1', 'Credit.1']

        merged_df = pd.DataFrame({
            'Course\nCode': df['Course\nCode'].tolist() + df['Course\nCode.1'].tolist(),
            'Course Title': df['Course Title'].tolist() + df['Course Title.1'].tolist(),
            'Grade': df['Grade'].tolist() + df['Grade.1'].tolist(),
            'Credit': df['Credit'].tolist() + df['Credit.1'].tolist()
        })

        merged_df = merged_df.dropna()
        rows_array = merged_df.to_numpy().tolist()

    return {
        "student" : {
            "English name" : student_english_name,
            "Thai name" : student_thai_name,
            "No" : student_id,
        },
        "subjects" : rows_array
    }