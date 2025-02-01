from sqlalchemy import Column, Integer, String, ForeignKey, PrimaryKeyConstraint, UniqueConstraint, ForeignKeyConstraint
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class enroll(Base):
    __tablename__ = "ENROLL"
    student_id = Column("StudentId", String, ForeignKey("STUDENT.StudentId"))
    course_id = Column("CourseId", String)
    course_name = Column("CourseName", String)
    enrollment_date = Column("EnrollmentDate", String)

    __table_args__ = (
        PrimaryKeyConstraint("StudentId", "CourseId", "CourseName"),
        ForeignKeyConstraint(["CourseId", "CourseName"], ["COURSE.CourseId", "COURSE.CourseName"], name="fk_course"),
    )


class SubjectTypeConf(Base):
    __tablename__ = "SUBJECT_TYPE_CONF"
    type_id = Column("TypeID", Integer, primary_key=True, index=True, autoincrement=True)
    type_name = Column("TypeName", String)
    least_credit_amount = Column("LeastCreditAmount", Integer)
    curriculum_year = Column("CurriculumYear", Integer)

    # relation with SUBJECT_GROUP
    has_group = relationship("SubjectGroup", back_populates="be_category_of")


class SubjectGroup(Base):
    __tablename__ = "SUBJECT_GROUP"
    group_name = Column("GroupName", String, primary_key=True, index=True)
    type_id = Column("TypeID", Integer, ForeignKey("SUBJECT_TYPE_CONF.TypeID"), nullable=False, index=True)
    least_credit_amount = Column("LeaestCreditAmount", Integer)  # Corrected the name

    # relation with SubjectTypeConf
    be_category_of = relationship("SubjectTypeConf", back_populates="has_group")
    # relation with Course
    has_subject = relationship("Course", back_populates="be_group_of")


class Course(Base):
    __tablename__ = "COURSE"
    course_id = Column("CourseId", String, index=True)
    course_name = Column("CourseName", String, index=True)
    group_name = Column("GroupName", String, ForeignKey("SUBJECT_GROUP.GroupName"), index=True)
    credit_amount = Column("CreditAmount", Integer)
    affiliation = Column("Affiliation", String)

    __table_args__ = (
        PrimaryKeyConstraint("CourseId", "CourseName"),
        UniqueConstraint("CourseId", "CourseName"),
    )

    def __str__(self):
        return f"{self.course_id}, {self.course_name}, {self.credit_amount}, {self.affiliation}, {self.group_name}"

    # relation with SubjectGroup
    be_group_of = relationship("SubjectGroup", back_populates="has_subject")

    # relation with Student
    students = relationship('Student', secondary="ENROLL", back_populates='courses')

class Student(Base):
    __tablename__ = "STUDENT"
    student_id = Column("StudentId", String, primary_key=True, index=True)
    student_english_name = Column("StudentEnglishName", String)
    student_thai_name = Column("StudentThaiName", String)
    faculty = Column("Faculty", String)

    # relation with Course
    courses = relationship('Course', secondary="ENROLL", back_populates='students')
