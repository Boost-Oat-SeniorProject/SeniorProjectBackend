from database.model import SubjectTypeConf, SubjectGroup, Course, Student, Enroll, UnfoundCourse
from database.database import SessionLocal
from sqlalchemy.orm import joinedload

def find_sum_credit(subjects):
    total = 0
    for course in subjects:
        total += course.creditAmount
    return total
        
def group_constraints(course):
    if course.beGroupOf.groupName == "Wellness":
        if (course.courseId).startswith("01175"):
            return False
    if course.beGroupOf.groupName == "LanguageandCommunication":
        if (course.courseId).startswith("013"):
            return False
    if course.beGroupOf.groupName == "ThaiCitizenandGlobalCitizen":
        if course.courseId == "01999111":
            return False
    if course.beGroupOf.groupName == "Elective":
        if course.courseId == "01418131":
            return False
    
    return True

def is_student_exist(db, info):
    # student = db.query(Student).options(joinedload(Student.courses), joinedload(Student.unfoundCourses)).filter(Student.studentId == info["studentId"]).first()
    student = db.query(Student).options(joinedload(Student.enrollments), joinedload(Student.unfoundCourses)).filter(Student.studentId == info["studentId"]).first()
    if student:
        return student
    return None

def update_course_to_db(db, info):
    # validate student if existed
    student = is_student_exist(db, info)
    if student is None:
        student = Student(studentId=info["studentId"], studentEnglishName=f"{info['englishName']['fullname']} {info['englishName']['lastname']}", studentThaiName=info["thaiName"], faculty=info["faculty"])
        db.add(student)
        db.commit()
        student = db.query(Student).options(joinedload(Student.enrollments), joinedload(Student.unfoundCourses)).filter_by(studentId=info["studentId"]).first()
    if student.enrollments:
        for course in student.enrollments:
            db.delete(course)
        for unfound_course in student.unfoundCourses:
            db.delete(unfound_course)
        db.commit()
        db.refresh(student)

    subjects = info["result"]
    for i in subjects:
        for course in i["courses"]:
            detail_course = db.query(Course).filter(Course.courseId==course["courseID"], Course.courseName==course["courseName"].replace(" ", "")).first()
            # validate if coursename is shorter than original
            if not detail_course:
                detail_course = db.query(Course).filter(Course.courseId==course["courseID"], Course.courseName.like(f"{course['courseName'].replace(' ', '')}%")).first()

            if detail_course:
                new_enrollment = Enroll(
                    studentId=student.studentId,
                    courseId=detail_course.courseId,
                    courseName=detail_course.courseName,
                    enrollmentDate=i["semester"],
                    grade=course["grade"]
                )
                db.add(new_enrollment)
            else:
                unfound_course = UnfoundCourse(
                    studentId=student.studentId,
                    courseId=course["courseID"],
                    courseName=course["courseName"],
                    enrollmentDate=i["semester"],
                    grade=course["grade"]
                )
                db.add(unfound_course)
    db.commit()
    print("insert completed")
    db.refresh(student)
    return student

def to_categories(info):
    db: Session = SessionLocal()
    student = update_course_to_db(db, info)

    all_groups = []
    subjectTypeConfs = db.query(SubjectTypeConf).all()
    for subjectTypeConf in subjectTypeConfs:
        subGroups = []
        if subjectTypeConf.typeName == "Open Electives":
            subGroups.append(
                {
                    "subGroupName" : "Open Electives",
                    "courses" : [],
                    "leastCreditAmount" : subjectTypeConf.leastCreditAmount,
                    "sumCreditAmount" : None,
                    "status" : False
                }
            )
        elif subjectTypeConf.hasGroup:
            for group in subjectTypeConf.hasGroup:
                tempSubGroups = {
                    "subGroupName" : group.groupName,
                    "courses" : [],
                    "leastCreditAmount" : group.leastCreditAmount,
                    "sumCreditAmount" : None,
                    "status" : False
                }
                subGroups.append(tempSubGroups)
        

        temp_group = {
            "groupName" : subjectTypeConf.typeName,
            "subGroups" : subGroups,
            "leastCreditAmount" : subjectTypeConf.leastCreditAmount,
            "sumCreditAmount" : None,
            "status" : False
        }
        all_groups.append(temp_group)

    groups = {}
    group_names = db.query(SubjectGroup).all()
    for group_name in group_names:
        groups[group_name.groupName] = {
            "courses" : [],
            "least_credit_amount" : group_name.leastCreditAmount,
            "sum_credit_amount" : None,
            "status" : False
        }
    
    for enrollment in student.enrollments:
        course = enrollment.course
        if enrollment.grade not in ['W', 'F', 'P']:
            if course.groupName in groups:
                groups[course.groupName]['courses'].append(course)

    for group_name in groups:
        groups[group_name]['courses'] = sorted(
            groups[group_name]['courses'],
            key=lambda course: course.creditAmount,
            reverse=True
        )

    # Separate to FacultyGECourses
    for group_name in groups:
        if group_name not in ["FacultyGECourses", "Coresubject", "RestrictedElective", "Elective"]:
            facultyGECoursesCredit = find_sum_credit(groups["FacultyGECourses"]['courses'])
            if facultyGECoursesCredit >= groups['FacultyGECourses']['least_credit_amount']:
                break
            for course in groups[group_name]['courses']:
                total = find_sum_credit(groups[group_name]['courses'])
                if total - course.creditAmount >= groups[group_name]['least_credit_amount']:
                    if group_constraints(course):
                        temp = course
                        groups[group_name]['courses'].remove(course)
                        groups['FacultyGECourses']['courses'].append(temp)

    # Separate to Open Electives
    temp_open_electives = []

    open_electives_data = None
    for group in all_groups:
        if group["groupName"] == "Open Electives":
            open_electives_data = group

    for group_name in groups:
        if group_name not in ["Coresubject", "RestrictedElective"]:
            total_credit_open_electives = find_sum_credit(temp_open_electives)
            if total_credit_open_electives >= open_electives_data["leastCreditAmount"]:
                break
            for course in groups[group_name]['courses']:
                total = find_sum_credit(groups[group_name]['courses'])
                if total - course.creditAmount >= groups[group_name]['least_credit_amount']:
                    if group_constraints(course):
                        temp = course
                        groups[group_name]['courses'].remove(course)
                        temp_open_electives.append(temp)

    # Calculate total credits of each group
    info["message"] = ""
    total_credits = 0
    graduated = True
    for group in groups:
        total = find_sum_credit(groups[group]['courses'])
        total_credits += total
        groups[group]["sum_credit_amount"] = total
        if total >= groups[group]['least_credit_amount']:
            groups[group]["status"] = True
        else:
            graduated = False
            info["message"] += f"{group}'s credits do not meet the minimum requirement.\n"

    open_electives_status = False
    total_credits_open_electives = find_sum_credit(temp_open_electives)
    if total_credit_open_electives >= open_electives_data["leastCreditAmount"]:
        open_electives_status = True
    total_credits += total_credits_open_electives
    
    # Map groups to all_groups
    for all_groups_group in all_groups:
        all_groups_sub_group_credit = 0
        all_groups_sub_group_status = True
        for all_groups_sub_group in all_groups_group["subGroups"]:
            for subGroup in groups:
                if all_groups_sub_group["subGroupName"] == subGroup:
                    all_groups_sub_group['courses'] = groups[subGroup]['courses']
                    all_groups_sub_group['sumCreditAmount'] = groups[subGroup]['sum_credit_amount']
                    all_groups_sub_group['status'] = groups[subGroup]['status']

                    all_groups_sub_group_credit += groups[subGroup]['sum_credit_amount']
                    all_groups_sub_group_status = all_groups_sub_group_status and groups[subGroup]['status']

        all_groups_group["sumCreditAmount"] = all_groups_sub_group_credit
        all_groups_group["status"] = all_groups_sub_group_status

    for all_groups_group in all_groups:
        for all_groups_sub_group in all_groups_group["subGroups"]:
            if all_groups_sub_group["subGroupName"] == "Open Electives":
                all_groups_sub_group["courses"] = temp_open_electives
                all_groups_sub_group["status"] = open_electives_status
                all_groups_sub_group["sumCreditAmount"] = total_credits_open_electives

                all_groups_sub_group_credit = groups[subGroup]['sum_credit_amount']
                all_groups_sub_group_status = all_groups_sub_group_status and groups[subGroup]['status']
        
        if all_groups_group['groupName'] == "Open Electives":
            all_groups_group["status"] = open_electives_status
            all_groups_group["sumCreditAmount"] = total_credits_open_electives

    info["result"] = all_groups
    info["totalCredit"] = total_credits
    info["notFoundCourses"] =  {
            "GroupName": "ไม่มีวิชาอยู่ในระบบ",
            "Course": [
                {
                    "courseName" : x.courseName,
                    "courseId" : x.courseId,
                    "grade" : x.grade,
                    "enrollmentDate" : x.enrollmentDate,
                } for x in student.unfoundCourses],
    }
    if student.unfoundCourses:
        info["isGraduated"] = False
        info["message"] = "The system cannot generate a conclusion because there are courses that are not found in the system."
    else:
        info["isGraduated"] = graduated


    return info