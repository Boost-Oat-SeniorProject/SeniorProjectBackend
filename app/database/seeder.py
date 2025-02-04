import pandas as pd
from sqlalchemy.orm import Session
from .database import SessionLocal
from .model import SubjectTypeConf, SubjectGroup, Course

SubjectTypeConfData = pd.read_csv("./database/SubjectTypeConfData.csv", dtype={'type_name':str, 'curriculum_year': str}).to_numpy().tolist()

SubjectGroupData = pd.read_csv("./database/SubjectGroupData.csv").to_numpy().tolist()

cs_courses = pd.read_csv("./database/cs_course.csv", dtype={'codeCourse': str})
other_courses = pd.read_csv("./database/result.csv", dtype={'codeCourse': str})


CourseData = pd.concat([cs_courses, other_courses], ignore_index=True)
CourseData = CourseData.drop("courseYear", axis=1)
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
            for data in SubjectGroupData:
                subject_type_conf = db.query(SubjectTypeConf).filter(SubjectTypeConf.type_name == data[2]).first()
                group = SubjectGroup(group_name=data[0], type_id=subject_type_conf.type_id, least_credit_amount=data[1])
                db.add(group)
            db.commit()
            print("seeding SubjectGroup is complete")    
        else:
            print("SubjectGroup data already exists.")
        if not db.query(Course).first():
            for data in CourseData:
                group = db.query(SubjectGroup).filter(SubjectGroup.group_name == data[4]).first()
                course = Course(course_id=data[0], course_name=data[1], group_name=group.group_name, credit_amount=data[2], affiliation=data[3])
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