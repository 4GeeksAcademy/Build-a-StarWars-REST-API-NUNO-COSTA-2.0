"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planets, People, Favorite
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/people', methods=['GET'])
def get_people():
    people = People.query.all()
    people_list = [{"id": person.id, "name": person.name} for person in people]
    return jsonify(people_list)


@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    person = People.query.get(people_id)
    if person is None:
        return jsonify({'message': 'Person not found'}), 404
    person_info = {"id": person.id, "name": person.name}
    return jsonify(person_info)


@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planets.query.all()
    planet_list = [{"id": planet.id, "name": planet.name}
                   for planet in planets]
    return jsonify(planet_list)


@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planets.query.get(planet_id)
    if planet is None:
        return jsonify({'message': 'Planet not found'}), 404
    planet_info = {"id": planet.id, "name": planet.name}
    return jsonify(planet_info)


@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    user_list = [{"id": user.id, "username": user.username} for user in users]
    return jsonify(user_list)


@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    user_id = 1
    favorites = Favorite.query.filter_by(user_id=user_id).all()
    favorite_list = [{"id": favorite.id, "planet_id": favorite.planet_id,
                      "people_id": favorite.people_id} for favorite in favorites]
    return jsonify(favorite_list)


@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    user_id = 1
    favorite = Favorite(user_id=user_id, planet_id=planet_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify({'message': 'Favorite planet added successfully'})


@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    user_id = 1
    favorite = Favorite(user_id=user_id, people_id=people_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify({'message': 'Favorite people added successfully'})


@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    user_id = 1
    favorite = Favorite.query.filter_by(
        user_id=user_id, planet_id=planet_id).first()
    if favorite is None:
        return jsonify({'message': 'Favorite planet not found'}), 404
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({'message': 'Favorite planet deleted successfully'})


@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    user_id = 1 
    favorite = Favorite.query.filter_by(
        user_id=user_id, people_id=people_id).first()
    if favorite is None:
        return jsonify({'message': 'Favorite people not found'}), 404
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({'message': 'Favorite people deleted successfully'})


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)