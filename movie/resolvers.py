import json
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from pymongo import MongoClient
from bson.json_util import dumps

client = MongoClient("mongodb://root:example@localhost:27017/")
db = client["movies"]

collection = db["movies"]
if collection.count_documents({}) == 0:
    with open('./data/movies.json', 'r') as file:
        movies = json.load(file)["movies"]
        collection.insert_many(movies)

def load_movies():
    collection = db["movies"]
    movies = list(collection.find({}, {"_id": 0}))
    return movies

def write_movies(movies):
    collection = db["movies"]
    collection.delete_many({})
    collection.insert_many(movies)

    movies = list(collection.find({}, {"_id": 0}))

    with open('./data/movies.json', 'w') as file:
        json.dump({'movies': movies}, file, indent=4)

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

def add_movie(_,info,_id,_title,_director,_rating):
    check_admin()
    movies = load_movies()
    for movie in movies:
        if movie['id'] == _id:
            raise Exception("movie ID already exists")
    new_movie = {'id': _id, 'title': _title, 'director': _director, 'rating': _rating}
    movies.append(new_movie)
    write_movies(movies)
    return new_movie

def update_movie_name(_,info,_id,_title):
    check_admin()
    movies = load_movies()
    for movie in movies:
        if movie['id'] == _id:
            movie['title'] = _title
            write_movies(movies)
            return movie
    raise Exception("movie ID not found")

def update_movie_rate(_,info,_id,_rate):
    check_admin()
    movies = load_movies()
    for movie in movies:
        if movie['id'] == _id:
            movie['rating'] = _rate
            write_movies(movies)
            return movie
    raise Exception("movie ID not found")

def delete_movie(_,info,_id):
    check_admin()
    movies = load_movies()
    for movie in movies:
        if movie['id'] == _id:
            movies.remove(movie)
            write_movies(movies)
            return movie
    raise Exception("movie ID not found")


def load_actors():
    with open('{}/data/actors.json'.format("."), "r") as file:
        return json.load(file)['actors']

def actor_with_id(_,info,_id):
    for actor in load_actors():
        if actor['id'] == _id:
            return actor

def resolve_actors_in_movie(movie, info):
    return [actor for actor in load_actors() if movie['id'] in actor['films']]
