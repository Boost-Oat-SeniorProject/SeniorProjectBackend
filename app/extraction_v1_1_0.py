import pdfplumber
import PyPDF2
import pandas as pd
import re
from fastapi.responses import JSONResponse
import header_extraction

def extract_subjects(pdf):
    text = ""
    try:
        reader = PyPDF2.PdfReader(pdf)
        if len(reader.pages) > 0:
            page = reader.pages[0]
            text = page.extract_text()
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": "Error reading PDF"}
        )
    # validate if this file is transcript
    patterns = {
        "university": re.compile(r".*kasetsart.*", re.IGNORECASE),
        "student_info": re.compile(r"Student.+No.+[0-9]{10}", re.IGNORECASE),
        "gpa": re.compile(r"G\.?P\.?A\.?", re.IGNORECASE),
        "institution": re.compile(r".*semester.*", re.IGNORECASE),
    }
    matches = {key: pattern.search(text) is not None for key, pattern in patterns.items()}
    if sum(matches.values()) < 2:
        return JSONResponse(
            status_code=400,
            content={"error": "The uploaded file does not appear to be a transcript."}
        )

    student_id, student_thai_name = header_extraction.extract(pdf)
    
    with pdfplumber.open(pdf) as pdf:
        first_page = pdf.pages[0]
        tables = first_page.extract_tables() 
        merged_df = pd.DataFrame()
        result = []
        if tables:
            # extract subjects for table
            for table in tables:
                df = pd.DataFrame(table)
                df.columns = df.iloc[0]  # Set the first row as column headers
                df = df[1:]  # Remove the header row
            
                if len(df.columns) == 8:
                    df.columns = ['Course\nCode', 'Course Title', 'Grade', 'Credit', 
                                'Course\nCode.1', 'Course Title.1', 'Grade.1', 'Credit.1']

                    merged_df = pd.DataFrame({
                        'CourseCode': df['Course\nCode'].tolist() + df['Course\nCode.1'].tolist(),
                        'Course Title': df['Course Title'].tolist() + df['Course Title.1'].tolist(),
                        'Grade': df['Grade'].tolist() + df['Grade.1'].tolist(),
                        'Credit': df['Credit'].tolist() + df['Credit.1'].tolist()
                    })
            merged_df = merged_df.dropna(how="all").reset_index(drop=True)
            merged_df = merged_df.to_numpy().tolist()

            # validate course name
            for index, data in enumerate(merged_df):
                if data[1] is not None:
                    if not data[1][0].isupper():
                        for i, s in enumerate(data[1]):
                            if s.isupper():
                                merged_df[index][1] = data[1][i:]
                                break

            temp_semester = {
                "semester" : None,
                'courses' : [],
                "sem_gpa" : None,
                "cum_gpa" : None
            }
            temp_course = {
                "courseID" : None,
                "courseName" : None,
                "grade" : None,
                "credit" : None
            }
            foundSemester = False
            for item in merged_df:
                sem = re.search(r'sem\. G\.P\.A\. = ', item[0])
                cum = re.search(r'cum\. G\.P\.A\. = ', item[0])
                if sem:
                    sem = re.search(r'sem\. G\.P\.A\. = (\d+\.\d+)', item[0])
                    cum = re.search(r'cum\. G\.P\.A\. = (\d+\.\d+)', item[0])
                    foundSemester = False
                    if sem:
                        sem_gpa = float(sem.group(1))
                        temp_semester['sem_gpa'] = sem_gpa
                    else:
                        temp_semester['sem_gpa'] = "-"
                    if cum:
                        cum_gpa = float(cum.group(1))
                        temp_semester['cum_gpa'] = cum_gpa
                    else:
                        temp_semester['cum_gpa'] = "-"
                    result.append(temp_semester)
                    temp_semester = temp_semester.fromkeys(temp_semester, None)
                    temp_semester['courses'] = []

                semester = re.search(r'.*(Semester|semester|Session|session).*', item[0])
                if semester:
                    temp_semester_format = semester.group()
                    temp_mapping = semester.group()
                    temp_mapping = temp_mapping.split(" ")
                    if temp_mapping[0].lower() == "first":
                        temp_semester_format = f"1/{str(temp_mapping[2])}"
                    elif temp_mapping[0].lower() == "second":
                        temp_semester_format = f"2/{str(temp_mapping[2])}"
                    elif temp_mapping[0].lower() == "summer":
                        temp_semester_format = f"summer/{str(temp_mapping[2])}"
                    temp_semester['semester'] = temp_semester_format
                    foundSemester = True
                elif foundSemester:
                    if item[0] is None or item[1] == None or item[2] == None or item[3] == None:
                        continue
                    temp_course['courseID'] = item[0]
                    temp_course['courseName'] = item[1]
                    temp_course['grade'] = item[2]
                    temp_course['credit'] = item[3]
                    temp_semester['courses'].append(temp_course)
                    # clear value
                    temp_course = temp_course.fromkeys(temp_course, None)



    return {
        "studentId" : student_id,
        "thaiName" : student_thai_name,
        "result" : result,
    }