import json
from db import Course, User, Assignment, db
from flask import Flask, request

app = Flask(__name__)
db_filename = "cms.db"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
with app.app_context():
    db.create_all()

def success_response(data, code=200):
    return json.dumps(data), code

def failure_response(message, code=404):
    return {"error": message}, code

# your routes here
@app.route("/")
def hello():
    return "Hello, World!"

@app.route("/api/courses/", methods=["GET"])
def get_courses():
    """
    Endpoint for getting all courses with assignments, instructors, and students
    """
    courses = [course.serialize() for course in Course.query.all()]
    return success_response(courses)

@app.route("/api/courses/", methods=["POST"])
def create_course():
    """
    Endpoint for creating a new course
    """
    body = json.loads(request.data)
    code = body.get("code")
    name = body.get("name")

    if code is None or name is None:
        return failure_response("Code and name are required to create a course.", 400)

    new_course = Course(code=code, name=name)
    db.session.add(new_course)
    db.session.commit()

    return success_response(new_course.serialize(), 201)

@app.route("/api/courses/<int:course_id>/", methods=["GET"])
def get_course(course_id):
    """
    Endpoint for getting a specific course by ID
    """
    course = Course.query.filter_by(id=course_id).first()
    if course is None:
        return failure_response("Course not found", 404)
    return success_response(course.serialize())

@app.route("/api/courses/<int:course_id>/",methods=["DELETE"])
def delete_course(course_id):
    """
    Endpoint for deleting a specific course by id
    """
    course = Course.query.filter_by(id=course_id).first()
    if course is None:
        return failure_response("Course not found", 404)
    
    db.session.delete(course)
    db.session.commit()
    return success_response(course.serialize())

@app.route("/api/users/", methods=["POST"])
def create_user():
    """
    Endpoint for creating a new user
    """
    body = json.loads(request.data)
    name = body.get("name")
    netid = body.get("netid")

    if name is None or netid is None:
        return failure_response("Name and netid are required to create a user.", 400)

    new_user = User(name=name, netid=netid)
    db.session.add(new_user)
    db.session.commit()

    return success_response(new_user.serialize(), 201)

@app.route("/api/users/<int:user_id>/", methods=["GET"])
def get_user(user_id):
    """
    Endpoint for getting a specific user by id
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found", 404)
    return success_response(user.serialize())

@app.route("/api/courses/<int:course_id>/add/", methods=["POST"])
def add_user_to_course(course_id):
    """
    Endpoint for adding a user to a course with a specific type (instructor or student)
    """
    body = json.loads(request.data)
    user_id = body.get("user_id")
    user_type = body.get("type")

    if user_id is None or user_type not in ["instructor", "student"]:
        return failure_response("Valid user_id and type ('instructor' or 'student') are required.", 400)

    course = Course.query.filter_by(id=course_id).first()
    if course is None:
        return failure_response("Course not found", 404)

    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found", 404)

    course.users.append(user)

    # Add the user to the course with the specified type
    stmt = db.association_table.insert().values(user_id=user.id, course_id=course.id, type=user_type)
    db.session.execute(stmt)
    db.session.commit()

    return success_response(Course.query.filter_by(id=course_id).first().serialize(), 200)

@app.route("/api/courses/<int:course_id>/assignments/", methods=["POST"])
def create_assignment(course_id):
    """
    Endpoint for creating a new assignment for a specific course
    """
    body = json.loads(request.data)
    title = body.get("title")
    due_date = body.get("due_date")

    if due_date is None or title is None:
        return failure_response("Due date and title are required to create an assignment.", 400)
    course = Course.query.filter_by(id=course_id).first()
    if course is None:
        return failure_response("Course not found", 404)

    new_assignment = Assignment(title=title, due_date=due_date, course_id=course.id)
    db.session.add(new_assignment)
    db.session.commit()

    return success_response(new_assignment.simple_serialize(), 201)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
