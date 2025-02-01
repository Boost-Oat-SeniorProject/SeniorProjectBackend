from database.model import SubjectTypeConf, SubjectGroup, Course
from database.database import SessionLocal

def find_sum_credit(groups, group_name):
    total = 0
    for course in groups[group_name]['courses']:
        total += course.credit_amount
    return total
        

def to_categories(info):
    db: Session = SessionLocal()

    subjects = info["result"]
    groups = {}
    group_names = db.query(SubjectGroup).all()
    for group_name in group_names:
        groups[group_name.group_name] = {
            "courses" : [],
            "least_credit_amount" : group_name.least_credit_amount,
            "sum_credit_amount" : None,
            "status" : False
        }
    FacultyGECourses = []

    # categorizes each courses
    not_found_in_db = []
    for i in subjects:
        print(i)
        for course in i["courses"]:
            if course["grade"] not in ['W', 'F', 'P']:
                detail_course = db.query(Course).filter(Course.course_id==course["courseID"], Course.course_name==course["courseName"].replace(" ", "")).first()
                if not detail_course:
                    detail_course = db.query(Course).filter(Course.course_id==course["courseID"], Course.course_name.like(f"{course['courseName'].replace(' ', '')}%")).first()

                if detail_course:
                    if detail_course.group_name in groups:
                        groups[detail_course.group_name]['courses'].append(detail_course)
                    if detail_course.affiliation == 'คณะวิทยาศาสตร์' and (detail_course.group_name not in ["Coresubject", "RestrictedElective", "Elective"]):
                        FacultyGECourses.append(detail_course)
                else:
                    not_found_in_db.append({
                        'course_name' : course["courseName"], 
                        'course_id' : course["courseID"]
                    })
    
    FacultyGECourses = sorted(
        FacultyGECourses, 
        key=lambda course: course.credit_amount
    )

    for course in FacultyGECourses:
        total = find_sum_credit(groups, course.group_name)
        currentFacultyGECourses = find_sum_credit(groups, 'FacultyGECourses')
        if currentFacultyGECourses >= groups['FacultyGECourses']['least_credit_amount']:
            break
        if total - course.credit_amount >= groups[course.group_name]['least_credit_amount']:
            temp = course
            groups[course.group_name]['courses'].remove(course)
            groups['FacultyGECourses']['courses'].append(temp)


    total_groups_credits = 0
    graduated = True
    for group in groups:
        total = find_sum_credit(groups, group)
        total_groups_credits += total
        groups[group]["sum_credit_amount"] = total
        if total >= groups[group]['least_credit_amount']:
            groups[group]["status"] = True
        else:
            graduated = False

    groups["total_groups_credits"] = total_groups_credits

    info["result"] = groups
    info["isGraduated"] = graduated
    info["not found courses"] = not_found_in_db

    return info
    # return groups, not_found_in_db