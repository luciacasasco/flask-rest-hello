# src/routes.py
from flask import Blueprint, jsonify, request
from models import db, User
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey, Table

api = Blueprint('api', __name__)

# --- MODELOS ADICIONALES ---

# Modelo Person
class Person(db.Model):
    __tablename__ = "person"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    gender: Mapped[str] = mapped_column(String(20))
    birth_year: Mapped[str] = mapped_column(String(20))

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "gender": self.gender,
            "birth_year": self.birth_year
        }

# Modelo Planet
class Planet(db.Model):
    __tablename__ = "planet"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    climate: Mapped[str] = mapped_column(String(120))
    population: Mapped[str] = mapped_column(String(50))

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "climate": self.climate,
            "population": self.population
        }

# --- TABLAS INTERMEDIAS ---

# User - Favorite People
user_favorite_people = Table(
    'user_favorite_people',
    db.Model.metadata,
    db.Column('user_id', Integer, ForeignKey('user.id')),
    db.Column('person_id', Integer, ForeignKey('person.id'))
)

# User - Favorite Planets
user_favorite_planets = Table(
    'user_favorite_planets',
    db.Model.metadata,
    db.Column('user_id', Integer, ForeignKey('user.id')),
    db.Column('planet_id', Integer, ForeignKey('planet.id'))
)

# --- ENDPOINTS ---

# PEOPLE
@api.route('/people', methods=['GET'])
def get_people():
    people = Person.query.all()
    return jsonify([p.serialize() for p in people]), 200

@api.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    person = Person.query.get_or_404(people_id)
    return jsonify(person.serialize()), 200

# PLANETS
@api.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    return jsonify([p.serialize() for p in planets]), 200

@api.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get_or_404(planet_id)
    return jsonify(planet.serialize()), 200

# USERS
@api.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([u.serialize() for u in users]), 200

# FAVORITES
@api.route('/users/favorites', methods=['GET'])
def get_favorites():
    user = User.query.first()
    if not user:
        return jsonify({"msg": "No user found"}), 404

    favorite_people = db.session.query(Person).join(user_favorite_people).filter(user_favorite_people.c.user_id == user.id).all()
    favorite_planets = db.session.query(Planet).join(user_favorite_planets).filter(user_favorite_planets.c.user_id == user.id).all()

    return jsonify({
        "people": [p.serialize() for p in favorite_people],
        "planets": [p.serialize() for p in favorite_planets]
    }), 200

# ADD FAVORITE PERSON
@api.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_person(people_id):
    user = User.query.first()
    person = Person.query.get_or_404(people_id)
    db.session.execute(user_favorite_people.insert().values(user_id=user.id, person_id=person.id))
    db.session.commit()
    return jsonify({"msg": f"{person.name} added to favorites"}), 201

# ADD FAVORITE PLANET
@api.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    user = User.query.first()
    planet = Planet.query.get_or_404(planet_id)
    db.session.execute(user_favorite_planets.insert().values(user_id=user.id, planet_id=planet.id))
    db.session.commit()
    return jsonify({"msg": f"{planet.name} added to favorites"}), 201

# DELETE FAVORITE PERSON
@api.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_person(people_id):
    user = User.query.first()
    db.session.execute(
        user_favorite_people.delete().where(
            (user_favorite_people.c.user_id == user.id) & 
            (user_favorite_people.c.person_id == people_id)
        )
    )
    db.session.commit()
    return jsonify({"msg": "Favorite person removed"}), 200

# DELETE FAVORITE PLANET
@api.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    user = User.query.first()
    db.session.execute(
        user_favorite_planets.delete().where(
            (user_favorite_planets.c.user_id == user.id) &
            (user_favorite_planets.c.planet_id == planet_id)
        )
    )
    db.session.commit()
    return jsonify({"msg": "Favorite planet removed"}), 200
