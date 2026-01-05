from flask import Blueprint, request, render_template, url_for, redirect, flash
from forms import AddForm
import requests
from decorators import admin_only

def to_embed_url(maps_url):
    """
    Converts a regular Google Maps URL (with @lat,lng) into an embeddable iframe URL.
    Example input:
        https://www.google.com/maps/place/Eiffel+Tower/@48.8584,2.2945,17z/
    Output:
        https://www.google.com/maps?q=48.8584,2.2945&z=15&output=embed
    """
    import re
    match = re.search(r'@([-\d.]+),([-\d.]+)', maps_url)
    if not match:
        return None
    lat, lng = match.groups()
    # Adjust zoom (default 15 is good for city-level)
    return f"https://www.google.com/maps?q={lat},{lng}&z=15&output=embed"

web_bp = Blueprint("web", __name__)


@web_bp.route("/")
def index():
    featured = requests.get(
        url_for('api.get_random', _external=True)
    ).json()

    recent = requests.get(
        url_for('api.get_recent', _external=True)
    ).json()

    return render_template(
        'index.html', 
        featured=featured, 
        recent=recent
    )


@web_bp.route("/all_cafes")
def show_all():
    all_cafes = requests.get(
        url_for('api.get_all', _external=True)
    ).json()

    return render_template(
        'all.html', 
        all=all_cafes
    )


@web_bp.route("/add_cafe", methods=['GET', 'POST'])
@admin_only
def add_new_cafe():
    form = AddForm()
    if form.validate_on_submit():
        payload = {field.name: field.data for field in form}

        api_url = url_for("api.add_cafe", _external=True)
        response = requests.post(api_url, data=payload)

        if response.status_code == 200:
            flash("Cafe added successfully!", "success")
            return redirect(url_for("web.show_all"))  # or wherever
        else:
            flash("Something went wrong while adding cafe.", "danger")

    return render_template(
        'add.html',
        form=form
    )


@web_bp.route('/search', methods=['GET'])
def search():
    return render_template('search.html')


@web_bp.route('/cafe/<int:cafe_id>', methods=['GET'])
def show_cafe(cafe_id):
    cafe_selected = requests.get(
        url_for('api.view_by_id', cafe_id=cafe_id, _external=True)
    ).json()
    embed_url = to_embed_url(cafe_selected['cafe']['map_url'])

    return render_template(
        'viewcafe.html',
        cafe_data=cafe_selected,
        embed_url=embed_url
    )


@web_bp.route('/edit/<int:cafe_id>', methods=['GET', 'POST'])
@admin_only
def edit_cafe(cafe_id):
    view_response = requests.get(
        url_for('api.view_by_id', cafe_id=cafe_id, _external=True)
    ).json()
    post_to_edit = view_response['cafe']
    form = AddForm(data=post_to_edit)

    if form.validate_on_submit():
        payload = {field.name: field.data for field in form}
        api_url = url_for('api.edit_cafe', cafe_id=cafe_id, _external=True)

        response_update = requests.patch(api_url, json=payload)
        
        if response_update.ok:
            flash('Cafe updated successfully!', 'success')
        else:
            flash('Error updating cafe.', 'danger')

        return redirect(url_for('web.show_cafe', cafe_id=cafe_id))

    return render_template(
        'add.html',
        form=form
    )


# @web_bp.route('/search_results', methods=['GET'])
# def search_cafe():
#     query = request.args.get('q')
#     cafes = []
#     if query:
#         search_result = requests.get(
#             url_for('api.search', query=query, _external=True)
#         )

#         if search_result.status_code == 200:
#             cafes = search_result.json()
#         else:
#             cafes = []

#     return render_template(
#         'search_results.html',
#         found_cafes=cafes
#     )