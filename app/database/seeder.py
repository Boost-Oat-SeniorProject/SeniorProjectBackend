import pandas as pd
from sqlalchemy.orm import Session
from .database import SessionLocal
from .model import SubjectTypeConf, SubjectGroup, Course

SubjectTypeConfData = pd.read_csv("./database/SubjectTypeConfData.csv", dtype={'type_name':str, 'type_name_th':str, 'curriculum_year': str}).to_numpy().tolist()

SubjectGroupData = pd.read_csv("./database/SubjectGroupData.csv").to_numpy().tolist()

cs_courses = pd.read_csv("./database/cs_course.csv", dtype={'codeCourse': str})
other_courses = pd.read_csv("./database/result.csv", dtype={'codeCourse': str})


CourseData = pd.concat([cs_courses, other_courses], ignore_index=True)
CourseData = CourseData.drop(["courseYear", "affiliation"], axis=1)
CourseData = CourseData.to_numpy().tolist()

def seed():
    db: Session = SessionLocal()
    print("make session with db successfully")

    try:
        if not db.query(SubjectTypeConf).first():
            for data in SubjectTypeConfData:
                subject_type_conf = SubjectTypeConf(typeName=data[0], typeNameTh=data[1], leastCreditAmount=data[2], curriculumYear=data[3])
                db.add(subject_type_conf)
            db.commit()
            print("seeding SubjectTypeConf is complete")
        else:
            print("SubjectTypeConf data already exists.")
        
        if not db.query(SubjectGroup).first():
            for data in SubjectGroupData:
                subject_type_conf = db.query(SubjectTypeConf).filter(SubjectTypeConf.typeName == data[3]).first()
                group = SubjectGroup(groupName=data[0], groupNameTh=data[1], typeId=subject_type_conf.typeId, leastCreditAmount=data[2])
                db.add(group)
            db.commit()
            print("seeding SubjectGroup is complete")    
        else:
            print("SubjectGroup data already exists.")
        if not db.query(Course).first():
            for data in CourseData:
                group = db.query(SubjectGroup).filter(SubjectGroup.groupName == data[3]).first()
                course = Course(courseId=data[0], courseName=data[1], groupName=group.groupName, creditAmount=data[2])
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