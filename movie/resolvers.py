import json
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from pymongo import MongoClient, ReturnDocument
from pymongo.errors import DuplicateKeyError

client = MongoClient("mongodb://root:example@mongo:27017/")
db = client["movies"]

collection = db["movies"]
if collection.count_documents({}) == 0:
    with open('./data/movies.json', 'r') as file:
        movies = json.load(file)["movies"]
        collection.insert_many(movies)
# deux films ne peuvent pas avoir le même id
collection.create_index("id", unique=True)

def load_movies():
    collection = db["movies"]
    movies = list(collection.find({}, {"_id": 0}))
    return movies

def check_admin():
    verify_jwt_in_request()
    if not get_jwt().get("admin", False):
        raise Exception("Admin permission required")

def all_movies(_,info):
    return load_movies()

def movie_with_id(_,info,_id):
    for movie in load_movies():
        if movie['id'] == _id:
            return movie

def movie_with_title(_,info,_title):
    for movie in load_movies():
        if movie['title'] == _title:
            return movie

# chaque mutation ne touche que le document concerné

def add_movie(_,info,_id,_title,_director,_rating):
    check_admin()
    new_movie = {'id': _id, 'title': _title, 'director': _director, 'rating': _rating}
    try:
        db["movies"].insert_one(new_movie)
    except DuplicateKeyError:
        raise Exception("movie ID already exists")
    return new_movie

def update_movie(_id, changes):
    movie = db["movies"].find_one_and_update(
        {'id': _id}, {'$set': changes},
        projection={"_id": 0}, return_document=ReturnDocument.AFTER)
    if not movie:
        raise Exception("movie ID not found")
    return movie

def update_movie_name(_,info,_id,_title):
    check_admin()
    return update_movie(_id, {'title': _title})

def update_movie_rate(_,info,_id,_rate):
    check_admin()
    return update_movie(_id, {'rating': _rate})

def delete_movie(_,info,_id):
    check_admin()
    movie = db["movies"].find_one_and_delete({'id': _id}, projection={"_id": 0})
    if not movie:
        raise Exception("movie ID not found")
    return movie

def load_actors():
    with open('{}/data/actors.json'.format("."), "r") as file:
        return json.load(file)['actors']

def actor_with_id(_,info,_id):
    for actor in load_actors():
        if actor['id'] == _id:
            return actor

def resolve_actors_in_movie(movie, info):
    return [actor for actor in load_actors() if movie['id'] in actor['films']]
