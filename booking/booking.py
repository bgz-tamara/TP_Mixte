from ariadne import graphql_sync, make_executable_schema, load_schema_from_path, ObjectType, QueryType, MutationType
from flask import Flask, request, jsonify, make_response
from flask_jwt_extended import JWTManager
import os

import resolvers as r

PORT = 3003
HOST = '0.0.0.0'
app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = os.environ.get(
    "JWT_SECRET_KEY", "dev-secret-change-this"
)

jwt = JWTManager(app)

# elements for Ariadne
type_defs = load_schema_from_path('booking.graphql')

query = QueryType()
query.set_field('all_bookings', r.all_bookings)
query.set_field('booking_with_userid', r.booking_with_userid)
query.set_field('booking_with_userid_date_movie', r.booking_with_userid_date_movie)

mutation = MutationType()
mutation.set_field('add_booking', r.add_booking)
mutation.set_field('delete_booking', r.delete_booking)

booking_date = ObjectType('BookingDate')
booking_date.set_field('movies', r.resolve_movies_in_date)
schema = make_executable_schema(type_defs, query, mutation, booking_date)

# root message
@app.route("/", methods=['GET'])
def home():
    return make_response("<h1 style='color:blue'>Welcome to the Booking service!</h1>",200)

# graphql entry points
@app.route('/graphql', methods=['POST'])
def graphql_server():
    data = request.get_json()
    success, result = graphql_sync(
        schema,
        data,
        context_value=None,
        debug=app.debug
    )
    status_code = 200 if success else 400
    return jsonify(result), status_code

if __name__ == "__main__":
    print("Server running in port %s"%(PORT))
    app.run(host=HOST, port=PORT)
