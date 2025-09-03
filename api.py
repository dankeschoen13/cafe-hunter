from flask import Blueprint, request, jsonify
from models import db, Cafe
from sqlalchemy import desc
import random

api_bp = Blueprint("api", __name__)

@api_bp.route('/random', methods=['GET'])
def get_random():
    cafe_objects = db.session.execute(
        db.select(Cafe)
    ).scalars().all()
    random_cafe = random.choice(cafe_objects)
    return jsonify(
        cafe=random_cafe.to_dict()
    )

@api_bp.route('/all', methods=['GET'])
def get_all():
    cafe_objects = db.session.execute(
        db.select(Cafe)
    ).scalars().all()
    return jsonify(
        [cafe.to_dict() for cafe in cafe_objects]
    )

@api_bp.route('/search', methods=['GET'])
def search_by_loc():
    location = request.args.get('loc')
    cafes_found = db.session.execute(
        db.select(Cafe)
        .where(Cafe.location == location)
    ).scalars().all()
    if cafes_found:
        return jsonify(
            [cafe.to_dict() for cafe in cafes_found]
        )
    else:
        return jsonify(
            error={'Not Found': "Sorry, we don't have a cafe at that location."}
        ), 404

@api_bp.route('/add', methods=['POST'])
def add_cafe():
    new_cafe_data = {key: request.form.get(key) for key in request.form}
    new_cafe = Cafe()
    for key, value in new_cafe_data.items():
        if value.lower() == 'true':
            setattr(new_cafe, key, True)
        elif value.lower() == 'false':
            setattr(new_cafe, key, False)
        else:
            setattr(new_cafe, key, value)
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(
        response={'success': "Successfully added the new cafe."}
    )

@api_bp.route('/update-price/<int:cafe_id>', methods=['PATCH'])
def update_price(cafe_id):
    new_price = request.form['price']
    try:
        cafe_to_update = db.session.get(Cafe, cafe_id)
        cafe_to_update.coffee_price = new_price
    except AttributeError:
        return jsonify(
            error={'Not Found': "Sorry a cafe with that id was not found in the database."}
        ), 404
    else:
        db.session.commit()
        return jsonify(
            success="Successfully updated the price."
        )

@api_bp.route('/report-closed/<int:cafe_id>', methods=['DELETE'])
def delete_cafe(cafe_id):
    if request.args.get('api-key') == 'TopSecretAPIKey':
        cafe_to_delete = db.session.get(Cafe, cafe_id)
        if cafe_to_delete is None:
            return jsonify(
                error={'Not Found': "Sorry a cafe with that id was not found in the database."}
            ), 404
        else:
            db.session.delete(cafe_to_delete)
            db.session.commit()
            return jsonify(
                success="Cafe has been deleted from the database."
            )
    else:
        return jsonify(
            error="Sorry, that's not allowed. Make sure you have the correct api_key."
        )

@api_bp.route('/recent', methods=['GET'])
def get_recent():
    recent_five = db.session.execute(
        db.select(Cafe).order_by(desc(Cafe.id)).limit(5)
    ).scalars().all()
    return jsonify([cafe.to_dict() for cafe in recent_five])
