import PyPDF2
import re

def pdf_to_text_first_page(pdf):
    # Open the PDF file
    text = ""
    reader = PyPDF2.PdfReader(pdf)
    if len(reader.pages) > 0:
        page = reader.pages[0]
        text = page.extract_text()
    return text

def extract_subjects(text):
    info = text.splitlines()
    cleaned_info = []
    for data in info:
        if data != ' ' or data != '\t':
            data = data.lstrip().rstrip()
            cleaned_info.append(data)

    isSemester = False
    detail = {}
    enrolled = []
    temp = []
    for data in cleaned_info:
        data = data.replace(' ', '') 

        '''
           1. search for word 'semester' in text 
           2. then find subject pattern
           3. stop finding for subject when find 'sem.G.P.A.'
        '''
        if isSemester:
            filtered = re.search("^[0-9]{8}.*[a|b|c|d|f|p|w|n]\+?[1-6]", data.lower())
            if filtered:
                #CodeCourse Title Grade Credit
                codeCourse = filtered.group()[0:8]

                filtered_more = re.search("[a|b|c|d|f|p|w|n]\+?[1-6]", filtered.group())

                title = filtered.group()[8:filtered_more.span()[0]]
                grade = filtered.group()[filtered_more.span()[0]:-1]
                credit = filtered.group()[-1] 
                temp.append([codeCourse, title, grade, credit])

        if re.search('.semester.', data.lower()) or re.search('^summer.*session', data.lower()):
            isSemester = True
            detail['semester'] = data
        elif re.search('^sem.*g\.p\.a\.', data.lower()):
            isSemester = False
            detail['gpa'] = data
            detail['enroll'] = temp.copy()
            enrolled.append(detail.copy())
            detail.clear()
            temp.clear()
    return enrolled

def extract_info(text):

    info = text.splitlines()
    cleaned_info = []
    for data in info:
        if data != ' ' or data != '\t':
            data = data.lstrip().rstrip()
            cleaned_info.append(data)

    thaiName = ""
    for data in cleaned_info:
        data = data.replace(' ', '') 
        #find thai name
        thai = re.search('[\u0E00-\u0E7F]+', data)
        
        if thai:
            thaiName += thai.group()

    thaiName = thaiName[:len(thaiName)-15]
    return thaiName
    
