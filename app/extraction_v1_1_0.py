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
    student_id = re.search('Student.+No.+[0-9]{10}', text)
    if student_id is None:
        student_id = ''
    else:
        student_id = student_id.group()[-10:]

    # extract faculty
    faculty = re.search('Faculty of +[A-Za-z]+', text)
    if faculty is None:
        faculty = ''
    else:
        faculty = faculty.group()
        faculty = faculty[11:]
        faculty = faculty.strip()

    # extract student's name
    english_name =  {
        "fullname": "",
        "lastname":""
    }
    student_english_name_match = re.search(r'(Miss|Mr\.).*?Field', text)
    if student_english_name_match:
        name_parts = student_english_name_match.group(0).split(' ')
        name_parts = [x for x in name_parts if x != 'Field']
        # skips Mr. or Miss
        student_english_name = "".join(name_parts[1:])
    
        # Extract surname (longest all-caps word in the name)
        if student_english_name:
            surname_match = re.findall(r'[A-Z]+', student_english_name)
            if surname_match:
                surname = max(surname_match, key=len)
                student_english_name = student_english_name.replace(surname, f" {surname}")
                names = student_english_name.split(' ')
                english_name['fullname'] = names[0]
                english_name['lastname'] = names[1]

    # extract student's Thai name
    student_thai_name = re.search(r'( *[\u0E00-\u0E7F]+ )+', text)
    if student_thai_name is None:
        student_thai_name = ''
    else:
        student_thai_name = student_thai_name.group().replace(' ', '')

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
                # sem = re.search(r'sem\. G\.P\.A\. = (\d+\.\d+)', item[0])
                # cum = re.search(r'cum\. G\.P\.A\. = (\d+\.\d+)', item[0])
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
                    temp_semester['semester'] = semester.group()
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
        "englishName" : english_name,
        "faculty" : faculty,
        "result" : result,
    }

# path = "../../../../Downloads/transcript_ยื่นจบ.pdf"
# path = '../../transcript_sample/6310401041.pdf'
# f = extract_subjects(path)
# print(f['english_name'])
# print(f['thai_name'])