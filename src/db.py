from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

association_table = db.Table(
    "course_user_association",
    db.Model.metadata,
    db.Column("course_id", db.Integer, db.ForeignKey("courses.id")),
    db.Column("user_id", db.Integer, db.ForeignKey("users.id")),
    db.Column("type", db.String, nullable=False)
)

class Course(db.Model):
    """
    Course model
    One-to-many relationship with Assignment model
    Many-to-many relationship with User model
    """
    __tablename__ = "courses"
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    code = db.Column(db.String,nullable=False,unique=True)
    name = db.Column(db.String,nullable=False)
    assignments = db.relationship("Assignment",cascade="delete")
    users = db.relationship("User",secondary=association_table,back_populates="courses")

    def __init__(self,**kwargs):
        """
        Initialize Course instance
        """
        self.code = kwargs.get("code")
        self.name = kwargs.get("name","")

    def serialize_simple(self):
        """
        Serialize Course instance without assignments or users
        """
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name
        }
    
    def get_course_users_by_type(self,user_type):
        """
        Get users of a specific type (instructor or student).
        Query the users via the association table so we can filter by the association 'type' column.
        """
        # Filter by `type` by joining the association table explicitly and filter on its columns.
        join_table = db.session.query(User).join(association_table, association_table.c.user_id == User.id)

        return join_table.filter(
            association_table.c.course_id == self.id,
            association_table.c.type == user_type
        ).all()

    def serialize(self):
        """
        Serialize Course instance with assignments and users
        """
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "assignments": [assignment.simple_serialize() for assignment in self.assignments],
            "instructors": [user.simple_serialize() for user in self.get_course_users_by_type("instructor")],
            "students": [user.simple_serialize() for user in self.get_course_users_by_type("student")]
        }

class User(db.Model):
    """
    User model
    Many-to-many relationship with Course model
    """
    __tablename__ = "users"
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    name = db.Column(db.String,nullable=False)
    netid = db.Column(db.String,nullable=False,unique=True)
    courses = db.relationship("Course",secondary=association_table,back_populates="users")

    def __init__(self,**kwargs):
        """
        Initialize User instance
        """
        self.name = kwargs.get("name","")
        self.netid = kwargs.get("netid")

    def simple_serialize(self):
        """
        Serialize User instance without course details
        """
        return {
            "id": self.id,
            "name": self.name,
            "netid": self.netid
        }

    def serialize(self):
        """
        Serialize User instance with course details
        """
        return {
            "id": self.id,
            "name": self.name,
            "netid": self.netid,
            "courses": [course.serialize_simple() for course in self.courses]
        }

class Assignment(db.Model):
    """
    Assignment model
    Many-to-one relationship with Course model
    """
    __tablename__ = "assignments"
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    title = db.Column(db.String,nullable=False)
    due_date = db.Column(db.Integer,nullable=False)
    course_id = db.Column(db.Integer,db.ForeignKey("courses.id"),nullable=False)

    def __init__(self,**kwargs):
        """
        Initialize Assignment instance
        """
        self.title = kwargs.get("title","")
        self.due_date = kwargs.get("due_date",0)
        self.course_id = kwargs.get("course_id")

    def simple_serialize(self):
        """
        Serialize Assignment instance without course details
        """
        return {
            "id": self.id,
            "title": self.title,
            "due_date": self.due_date
        }
    