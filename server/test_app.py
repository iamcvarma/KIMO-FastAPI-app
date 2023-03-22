from fastapi.testclient import TestClient
import mongomock
import pytest

from main import app, collection

@pytest.fixture
def client():
    # Use mongomock to create a temporary in-memory MongoDB instance for testing
    client = mongomock.MongoClient()

    db = client["test_database"]

    collection = db["test_collection"]

    # Insert test data into the collection
    test_data =[
  {
    "_id":"course1",
    "name": "Introduction to Python",
    "date": 1648107366,
    "description": "Learn the basics of Python programming language.",
    "domain": ["Programming"],
    "chapters": [
      {
        "_id": "chapter1",
        "name": "Python Basics",
        "contents": "This chapter covers the basics of Python syntax and data types.",
        "rating": 2
      },
      {
        "_id": "chapter2",
        "name": "Functions and Control Flow",
        "contents": "This chapter covers functions and control flow statements in Python.",
        "rating": 2
      }
    ],
    "rating": 2
  },
  {
    "_id":"course2",
    "name": "Web Development with Flask",
    "date": 1648107399,
    "description": "Build web applications using Flask framework.",
    "domain": ["Web Development"],
    "chapters": [
      {
        "_id": "chapter1",
        "name": "Flask Basics",
        "contents": "This chapter covers the basics of Flask framework.",
        "rating": 2
      },
      {
        "_id": "chapter2",
        "name": "RESTful APIs with Flask",
        "contents": "This chapter covers how to build RESTful APIs with Flask.",
        "rating": 2
      }
    ],
    "rating": 2
  }
]
    collection.insert_many(test_data)
    # Create a test client using the FastAPI app
    with TestClient(app) as client:
        yield client
    # After the tests are done, drop the test collection
    collection.drop()

def test_get_courses(client):
    response = client.get("/courses")
    assert response.status_code == 200
    courses = response.json()
    assert len(courses) == 2

def test_get_courses_alphabetical(client):
    response = client.get("/courses?sort=alphabetical")
    assert response.status_code == 200
    courses = response.json()
    assert len(courses) == 2
    assert courses[0]["name"] == "Introduction to Python"

def test_get_courses_filtered(client):
    response = client.get("/courses?domain=Programming")
    assert response.status_code == 200
    courses = response.json()
    assert len(courses) == 1
    assert courses[0]["name"] == "Introduction to Python"

def test_get_courses_sorted(client):
    response = client.get("/courses?sort=date")
    assert response.status_code == 200
    courses = response.json()
    assert len(courses) == 2
    assert courses[0]["name"] == "Web Development with Flask"
    assert courses[1]["name"] == "Introduction to Python"
   

def test_get_course(client):
    response = client.get("/courses/course1")
    assert response.status_code == 200
    course = response.json()
    assert course["name"] == "Introduction to Python"

def test_get_course_not_found(client):
    response = client.get("/courses/course3")
    assert response.status_code == 404

def test_get_chapter(client):
    response = client.get("/courses/course1/chapter5")
    assert response.status_code == 404


def test_rate_chapter_inc(client):
    response = client.post("/courses/course1/chapter1/rating?rating=1")
    assert response.status_code == 200
    message = response.json()
    assert message == {"message": "Rating added successfully."}

    # Check that the rating was added to the database
    course = collection.find_one({"_id":"course1"})
    assert course["chapters"][0]["rating"] == 3
    assert course["rating"] == 3

def test_rate_chapter_dec(client):
    response = client.post("/courses/course1/chapter1/rating?rating=-1")
    assert response.status_code == 200
    message = response.json()
    assert message == {"message": "Rating added successfully."}

    # Check that the rating was added to the database
    course = collection.find_one({"_id":"course1"})
    assert course["chapters"][0]["rating"] == 2
    assert course["rating"] == 2


