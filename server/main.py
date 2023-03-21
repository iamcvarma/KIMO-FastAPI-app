from fastapi import FastAPI,HTTPException
from pymongo import MongoClient,ASCENDING,DESCENDING

app = FastAPI()

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client["mydatabase"]
collection = db["courses"]


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/courses")
async def get_courses(sort: str = 'alphabetical', domain: str = None):
    """
    Get a list of all available courses, sorted and optionally filtered by domain.
    """
    # Set up sort order and query filter based on input parameters
    if sort=='alphabetical':
        sort_key = 'name'
    elif sort=='date':
        sort_key = 'date'
    elif sort == "rating":
        sort_key = "rating"

    sort_dir = ASCENDING if sort == 'alphabetical' else DESCENDING
    
    filter_query = {}
    
    if domain:
        filter_query['domain'] = domain
    
    data = collection.find(filter_query).sort(sort_key,sort_dir)

    res = []
    for course in data:
        course["_id"] = str(course["_id"])
        res.append(course)
    return res


@app.get("/courses/{course_id}")
async def get_course(course_id: str):
    """
    Get the overview information for a specific course.
    """
    course = collection.find_one({'_id': course_id})
    if not course:
        raise HTTPException(status_code=404,detail="Course is not found")
    return course


@app.get("/courses/{course_id}/{chapter_id}")
async def get_chapter(course_id: str, chapter_id: str):
    course = collection.find_one({'_id': course_id})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    chapter = None
    for curr_chapter in course["chapters"]:
        if curr_chapter['_id']==chapter_id:
            chapter= curr_chapter
            break
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    return chapter

@app.post("/courses/{course_id}/{chapter_id}/rating")
async def rate_chapter(course_id: str, chapter_id: str, rating: int):
    course = collection.find_one({"_id": course_id})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    chapter = None
    for curr_chapter in course["chapters"]:
        if curr_chapter['_id']==chapter_id:
            chapter= curr_chapter
            break
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    collection.update_one({"_id": course_id, "chapters._id": chapter_id}, {"$inc": {"chapters.$.rating": rating}})
    collection.update_one({"_id": course_id}, {"$inc": {"rating": rating}})
    return {"message": "Rating added successfully."}
