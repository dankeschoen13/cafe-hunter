import os
from flask import Blueprint, request, jsonify
from app.constants import Errors, Alerts
from app.services import CafeService
from app.utils import get_clean_payload


api_bp = Blueprint("api", __name__)

@api_bp.get('/cafes/all')
def cafes_index():
    all_cafes = CafeService.fetch_all()

    if not all_cafes:
        return jsonify(
            error={'Not Found': Errors.NO_DATA_FOUND}
        ), 404

    return jsonify(
        [cafe.to_dict() for cafe in all_cafes]
    ), 200


@api_bp.get('/cafes/random')
def random():
    random_cafe = CafeService.fetch_random()

    if not random_cafe:
        return jsonify(
            error={'Not Found': Errors.NO_DATA_FOUND}
        ), 404

    return jsonify(
        cafe=random_cafe.to_dict()
    ), 200


@api_bp.get('/cafes/featured')
def featured():
    featured_cafes = CafeService.fetch_featured()

    if not featured_cafes:
        return jsonify(
            error={'Not Found': Errors.FEATURED_NOT_FOUND}
        ), 404

    return jsonify(
        [cafe.to_dict() for cafe in featured_cafes]
    ), 200


@api_bp.get('/cafes/recent')
def recent():
    requested_limit = request.args.get('limit', default=5, type=int)
    final_limit = min(requested_limit, 20)

    recent_cafes = CafeService.fetch_recent(final_limit)

    if not recent_cafes:
        return jsonify(
            error={'Not Found': Errors.NO_DATA_FOUND}
        ), 404

    return jsonify(
        [cafe.to_dict() for cafe in recent_cafes]
    ), 200


@api_bp.get('/cafes/<int:cafe_id>/show-details/')
def show(cafe_id):
    selected_cafe = CafeService.fetch_by_id(cafe_id)

    if not selected_cafe:
        return jsonify(
            error={'Not Found': Errors.ID_NOT_FOUND}
        ), 404

    return jsonify(
        cafe=selected_cafe.to_dict()
    )


@api_bp.get('/cafes/search')
def search():
    query = request.args.get('query')

    if not query or query.strip() == '':
        return jsonify(
            error={'Bad Request': 'Search query cannot be empty.'}
        ), 400

    cafes_found = CafeService.search(query)

    if cafes_found:
        return jsonify(
            [cafe.to_dict() for cafe in cafes_found]
        )
    else:
        return jsonify(
            error={'Not Found': Errors.RESULTS_NOT_FOUND}
        ), 404


@api_bp.post('/cafes/add')
def add():
    raw_data = get_clean_payload()

    try:
        new_cafe = CafeService.create(raw_data)
    except ValueError as e:
        return jsonify(
            error={'Conflict': str(e)}
        ), 409

    return jsonify(
        response={
            'success': Alerts.CAFE_ADDED,
            'cafe_id': new_cafe.id
        }
    ), 201


@api_bp.patch('/cafes/<int:cafe_id>/update')
def update(cafe_id):
    updated_data = get_clean_payload()

    try:
        updated_cafe = CafeService.update(updated_data, cafe_id)
    except ValueError as e:
        return jsonify(
            error={'Bad Request': str(e)}
        ), 409

    if not updated_cafe:
        return jsonify(
            error={'Not Found': Errors.ID_NOT_FOUND}
        ), 404

    return jsonify(
        response={
            'success': Alerts.CAFE_UPDATED,
            'cafe_id': updated_cafe.id
        }
    ), 201


@api_bp.patch('/cafes/<int:cafe_id>/report-closed')
def report_closed(cafe_id):
    try:
        reported_cafe = CafeService.report_closed(cafe_id)

    except ValueError as e:
        return jsonify(
            error={"Internal Server Error": str(e)}
        ), 500

    if not reported_cafe:
        return jsonify(
            error={"Not Found": Errors.ID_NOT_FOUND}
        ), 404

    tally = reported_cafe.closed_reports

    return jsonify(
        response={"success": f"{Alerts.CAFE_REPORTED}: {tally}"}
    ), 200


@api_bp.delete('/cafes/delete/<int:cafe_id>')
def delete_cafe(cafe_id):
    if request.args.get('api-key') == os.environ.get('API_KEY'):
        cafe_deleted = CafeService.delete(cafe_id)
        if not cafe_deleted:
            return jsonify(
                error={'Not Found': Errors.ID_NOT_FOUND}
            )
        return jsonify(
            success=Alerts.CAFE_DELETED
        )
    else:
        return jsonify(
            error=Errors.WRONG_API_KEY
        ), 403
