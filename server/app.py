#!/usr/bin/env python3

from flask import Flask, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


@app.route("/heroes")
def get_heroes():
    heroes = Hero.query.all()
    heroes_dict = [hro.to_dict(rules=("-hero_powers",)) for hro in heroes]

    return make_response(heroes_dict, 200)


@app.route("/heroes/<int:id>")
def retreive_hero(id):
    hero = Hero.query.filter_by(id=id).first()

    if not hero:
        response_body = {"error": "Hero not found"}
        return make_response(response_body, 404)

    hero_dict = hero.to_dict()
    return make_response(hero_dict, 200)


@app.route("/powers")
def get_powers():
    powers_list = Power.query.all()
    powers_dict = [p.to_dict(rules=('-hero_powers',)) for p in powers_list]
    return make_response(powers_dict, 200)


@app.route("/powers/<int:id>", methods=["GET", "PATCH"])
def retreive_power(id):
    # power = Power.query.filter_by(id=id).first()
    power = Power.query.get(id)

    if not power:
        response_body = {"error": "Power not found"}
        return make_response(response_body, 404)

    if request.method == "GET":
        response_body = power.to_dict(rules=('-hero_powers',))
        return make_response(response_body, 200)

    elif request.method == "PATCH":
        #validation
        description = request.form.get("description")       #get description from form data

        # if description:
        #     if not isinstance(description,str) or len(description) < 20:
        #         return make_response({"error": "Description must be at least 20 characters long"}, 400)
        if description is None or not isinstance(description, str) or len(description) < 20:
            return make_response({"errors": ["validation errors"]}, 400)

        
        for attr in request.form:
            setattr(power, attr, request.form.get(attr))
        db.session.commit()
        response_body = power.to_dict(only=('description','id','name'))
        return make_response(response_body,200)


@app.route("/hero_powers", methods=['POST'])
def add_hero_powers():
    #is request a form or JSON
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    #Validate 'strong' input from form
    strength = data.get('strength')
    if strength not in ['Strong','Weak','Average']:
        response_body = {"errors": ["validation errors"]}
        return make_response(response_body,400)
    
    #new Hero_Power instance
    new_h_p = HeroPower(strength =strength,hero_id =data.get('hero_id'),power_id = data.get('power_id'))
    
    #if Hero_Power is created successfully
    if new_h_p:
        db.session.add(new_h_p)
        db.session.commit()
        return make_response(new_h_p.to_dict(),200)
    elif not new_h_p:
        response_body = {"errors": ["validation errors"]}
        return make_response(response_body,400)


if __name__ == "__main__":
    app.run(port=5555, debug=True)
