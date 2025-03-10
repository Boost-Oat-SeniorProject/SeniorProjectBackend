from sqlalchemy import Column, Integer, String, Float, ForeignKey, PrimaryKeyConstraint, UniqueConstraint, ForeignKeyConstraint, CheckConstraint
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Enroll(Base):
    __tablename__ = "ENROLL"
    # enrollId = Column("Id", Integer, autoincrement=True)
    studentId = Column("StudentId", String, ForeignKey("STUDENT.StudentId"))
    courseId = Column("CourseId", String)
    courseName = Column("CourseName", String)
    enrollmentDate = Column("EnrollmentDate", String)
    grade = Column("Grade", String(2))

    __table_args__ = (
        # PrimaryKeyConstraint("Id", "StudentId", "CourseId", "CourseName"),
        PrimaryKeyConstraint("StudentId", "CourseId", "CourseName", "Grade"),
        ForeignKeyConstraint(["CourseId", "CourseName"], ["COURSE.CourseId", "COURSE.CourseName"], name="fk_course", ondelete="CASCADE"),
    )

    student = relationship("Student", back_populates="enrollments") 
    course = relationship("Course", primaryjoin="and_(Enroll.courseId == Course.courseId, Enroll.courseName == Course.courseName)", backref="enrollments")

class UnfoundCourse(Base):
    __tablename__ = "UNFOUND_COURSE"
    studentId = Column("StudentId", String, ForeignKey("STUDENT.StudentId", ondelete="CASCADE"))
    courseId = Column("CourseId", String)
    courseName = Column("CourseName", String)
    enrollmentDate = Column("EnrollmentDate", String)
    grade = Column("Grade", String(2))
    creditAmount = Column("CreditAmount", Integer)

    __table_args__ = (
        PrimaryKeyConstraint("StudentId", "CourseId", "CourseName"),
    )

    belongsTo = relationship("Student", back_populates="unfoundCourses")

class SubjectTypeConf(Base):
    __tablename__ = "SUBJECT_TYPE_CONF"
    typeId = Column("TypeID", Integer, primary_key=True, index=True, autoincrement=True)
    typeName = Column("TypeName", String)
    typeNameTh = Column("TypeNameTh", String)
    leastCreditAmount = Column("LeastCreditAmount", Integer)
    curriculumYear = Column("CurriculumYear", Integer)

    # relation with SUBJECT_GROUP
    hasGroup = relationship("SubjectGroup", back_populates="beCategoryOf")


class SubjectGroup(Base):
    __tablename__ = "SUBJECT_GROUP"
    groupName = Column("GroupName", String, primary_key=True, index=True)
    groupNameTh = Column("GroupNameTh", String)
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

    # relation with SubjectGroup
    beGroupOf = relationship("SubjectGroup", back_populates="hasSubject")


class Student(Base):
    __tablename__ = "STUDENT"
    studentId = Column("StudentId", String, primary_key=True, index=True)
    studentThaiName = Column("StudentThaiName", String)
    gpa = Column("Gpa", Float, default=0.0)

    enrollments = relationship("Enroll", back_populates="student")

    # relation with Unfound
    unfoundCourses = relationship('UnfoundCourse', back_populates="belongsTo")
