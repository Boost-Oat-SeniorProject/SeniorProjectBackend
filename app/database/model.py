from sqlalchemy import Column, Integer, String, ForeignKey, PrimaryKeyConstraint, UniqueConstraint, ForeignKeyConstraint
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class enroll(Base):
    __tablename__ = "ENROLL"
    studentId = Column("StudentId", String, ForeignKey("STUDENT.StudentId"))
    courseId = Column("CourseId", String)
    courseName = Column("CourseName", String)
    enrollmentDate = Column("EnrollmentDate", String)

    __table_args__ = (
        PrimaryKeyConstraint("StudentId", "CourseId", "CourseName"),
        ForeignKeyConstraint(["CourseId", "CourseName"], ["COURSE.CourseId", "COURSE.CourseName"], name="fk_course"),
    )


class SubjectTypeConf(Base):
    __tablename__ = "SUBJECT_TYPE_CONF"
    typeId = Column("TypeID", Integer, primary_key=True, index=True, autoincrement=True)
    typeName = Column("TypeName", String)
    leastCreditAmount = Column("LeastCreditAmount", Integer)
    curriculumYear = Column("CurriculumYear", Integer)

    # relation with SUBJECT_GROUP
    hasGroup = relationship("SubjectGroup", back_populates="beCategoryOf")


class SubjectGroup(Base):
    __tablename__ = "SUBJECT_GROUP"
    groupName = Column("GroupName", String, primary_key=True, index=True)
    typeId = Column("TypeID", Integer, ForeignKey("SUBJECT_TYPE_CONF.TypeID"), nullable=False, index=True)
    leastCreditAmount = Column("LeaestCreditAmount", Integer)  # Corrected the name

    # relation with SubjectTypeConf
    beCategoryOf = relationship("SubjectTypeConf", back_populates="hasGroup")
    # relation with Course
    hasSubject = relationship("Course", back_populates="beGroupOf")


class Course(Base):
    __tablename__ = "COURSE"
    courseId = Column("CourseId", String, index=True)
    courseName = Column("CourseName", String, index=True)
    groupName = Column("GroupName", String, ForeignKey("SUBJECT_GROUP.GroupName"), index=True)
    creditAmount = Column("CreditAmount", Integer)

    __table_args__ = (
        PrimaryKeyConstraint("CourseId", "CourseName"),
        UniqueConstraint("CourseId", "CourseName"),
    )

    def __str__(self):
        return f"{self.course_id}, {self.course_name}, {self.credit_amount}, {self.affiliation}, {self.group_name}"

    # relation with SubjectGroup
    beGroupOf = relationship("SubjectGroup", back_populates="hasSubject")

    # relation with Student
    students = relationship('Student', secondary="ENROLL", back_populates='courses')

class Student(Base):
    __tablename__ = "STUDENT"
    studentId = Column("StudentId", String, primary_key=True, index=True)
    studentEnglishName = Column("StudentEnglishName", String)
    studentThaiName = Column("StudentThaiName", String)
    faculty = Column("Faculty", String)

    # relation with Course
    courses = relationship('Course', secondary="ENROLL", back_populates='students')
