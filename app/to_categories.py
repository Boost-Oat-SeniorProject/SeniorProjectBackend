from database.model import SubjectTypeConf, SubjectGroup, Course
from database.database import SessionLocal

def find_sum_credit(subjects):
    total = 0
    for course in subjects:
        total += course.credit_amount
    return total
        
def group_constraints(course):
    if course.be_group_of.group_name == "Wellness":
        if (course.course_id).startswith("01175"):
            return False
    if course.be_group_of.group_name == "LanguageandCommunication":
        if (course.course_id).startswith("013"):
            return False
    if course.be_group_of.group_name == "ThaiCitizenandGlobalCitizen":
        if course.course_id == "01999111":
            return False
    if course.be_group_of.group_name == "Elective":
        if course.course_id == "01418131":
            return False
    
    return True
        

def to_categories(info):
    db: Session = SessionLocal()

    all_groups = {}
    subjectTypeConfs = db.query(SubjectTypeConf).all()
    for sub in subjectTypeConfs:
        all_groups[sub.type_name] = {}
        all_groups[sub.type_name]['sub_groups'] = {}
        if not sub.has_group:
            all_groups[sub.type_name]["courses"] = []
        all_groups[sub.type_name]["least_credit_amount"] = sub.least_credit_amount
        for group in sub.has_group:
            all_groups[sub.type_name]['sub_groups'][group.group_name] = {}


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
    # categorizes each courses
    not_found_in_db = []
    subjects = info["result"]
    for i in subjects:
        for course in i["courses"]:
            if course["grade"] not in ['W', 'F', 'P']:
                detail_course = db.query(Course).filter(Course.course_id==course["courseID"], Course.course_name==course["courseName"].replace(" ", "")).first()
                if not detail_course:
                    detail_course = db.query(Course).filter(Course.course_id==course["courseID"], Course.course_name.like(f"{course['courseName'].replace(' ', '')}%")).first()

                if detail_course:
                    if detail_course.group_name in groups:
                        groups[detail_course.group_name]['courses'].append(detail_course)
                else:
                    not_found_in_db.append({
                        'course_name' : course["courseName"], 
                        'course_id' : course["courseID"]
                    })

    for group_name in groups:
        groups[group_name]['courses'] = sorted(
            groups[group_name]['courses'],
            key=lambda course: course.credit_amount,
            reverse=True
        )

    # Separate to FacultyGECourses
    for group_name in groups:
        if group_name not in ["FacultyGECourses", "Coresubject", "RestrictedElective", "Elective"]:
            facultyGECoursesCredit = find_sum_credit(groups['FacultyGECourses']['courses'])
            if facultyGECoursesCredit >= groups['FacultyGECourses']['least_credit_amount']:
                break
            for course in groups[group_name]['courses']:
                total = find_sum_credit(groups[group_name]['courses'])
                if total - course.credit_amount >= groups[group_name]['least_credit_amount']:
                    if group_constraints(course):
                        temp = course
                        groups[group_name]['courses'].remove(course)
                        groups['FacultyGECourses']['courses'].append(temp)

    # Separate to Open Electives
    temp_open_electives = []
    for group_name in groups:
        if group_name not in ["Coresubject", "RestrictedElective"]:
            total_credit = find_sum_credit(groups[group_name]['courses'])
            total_credit_open_electives = find_sum_credit(temp_open_electives)
            if total_credit_open_electives >= all_groups["Open Electives"]["least_credit_amount"]:
                break
            for course in groups[group_name]['courses']:
                total = find_sum_credit(groups[group_name]['courses'])
                if total - course.credit_amount >= groups[group_name]['least_credit_amount']:
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

    total_credits_open_electives = find_sum_credit(temp_open_electives)
    total_credits += total_credits_open_electives

    # Map groups to all_groups
    for group in groups:
        for key in all_groups.keys():
            for subkeys in all_groups[key]['sub_groups'].keys():
                if group in subkeys:
                    all_groups[key]['sub_groups'][group] = groups[group]
    all_groups["Open Electives"]["courses"] = temp_open_electives
    all_groups["Open Electives"]["sum_credit_amount"] = total_credits_open_electives
    

    info["result"] = all_groups
    info["total credit"] = total_credits
    info["not found courses"] = not_found_in_db
    if not_found_in_db:
        info["isGraduated"] = False
        info["message"] = "The system cannot generate a conclusion because there are courses that are not found in the system."
    else:
        info["isGraduated"] = graduated

    return info