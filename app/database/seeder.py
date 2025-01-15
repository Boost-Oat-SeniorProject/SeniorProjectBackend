import pandas as pd
from sqlalchemy.orm import Session
from .database import SessionLocal
from .model import SubjectTypeConf, SubjectGroup, Course

SubjectTypeConfData = [
    ["General Education Courses", 30, "2560"],
    ["Major Courses", 92, "2560"],
    ["Open Electives", 6, "2560"]
]

GeneralGroupData = [
    ["Wellness", 3],
    ["Entrepreneurship", 3],
    ["LanguageandCommunication", 13],
    ["ThaiCitizenandGlobalCitizen", 3],
    ["Aesthetics", 3],
]

MajorGroupData = [
    ["Coresubject", 16],
    ["RestrictedElective", 55],
    ["Elective", 21]
]

cs_courses = pd.read_csv("./database/cs_course.csv", dtype={'codeCourse': str})
other_courses = pd.read_csv("./database/complete_courses.csv", dtype={'codeCourse': str})


cs_courses = cs_courses.drop("courseYear", axis=1)
CourseData = pd.concat([cs_courses, other_courses], ignore_index=True)
CourseData = CourseData.to_numpy().tolist()

def seed():
    db: Session = SessionLocal()
    print("make session with db successfully")

    try:
        if not db.query(SubjectTypeConf).first():
            for data in SubjectTypeConfData:
                subject_type_conf = SubjectTypeConf(type_name=data[0], least_credit_amount=data[1], curriculum_year=data[2])
                db.add(subject_type_conf)
            db.commit()
            print("seeding SubjectTypeConf is complete")
        else:
            print("SubjectTypeConf data already exists.")
        
        if not db.query(SubjectGroup).first():
            general = db.query(SubjectTypeConf).filter(SubjectTypeConf.type_name == "General Education Courses").first()
            for data in GeneralGroupData:
                group = SubjectGroup(group_name=data[0], type_id=general.type_id, least_credit_amount=data[1])
                db.add(group)
            db.commit()
            major = db.query(SubjectTypeConf).filter(SubjectTypeConf.type_name == "Major Courses").first()
            for data in MajorGroupData:
                group = SubjectGroup(group_name=data[0], type_id=major.type_id, least_credit_amount=data[1])
                db.add(group)
            db.commit()
            print("seeding SubjectGroup is complete")    
        else:
            print("SubjectGroup data already exists.")
        if not db.query(Course).first():
            for data in CourseData:
                group = db.query(SubjectGroup).filter(SubjectGroup.group_name == data[3]).first()
                course = Course(course_id=data[0], course_name=data[1], group_name=group.group_name, credit_amount=data[2])
                db.add(course)
            db.commit()     
            print("seeding Course is complete")    
        else:
            print("Course data already exists.")

        
    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()