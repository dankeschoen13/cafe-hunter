from flask import Blueprint, request, render_template, url_for, redirect, flash
from forms import AddForm
import requests

web_bp = Blueprint("web", __name__)

@web_bp.route("/")
def index():
    return render_template('index.html')

@web_bp.route("/cafes")
def cafes_page():
    response = requests.get(
        url_for('api.get_all', _external=True)
    )
    cafes = response.json()
    return cafes

@web_bp.route("/beta")
def beta():
    response_random = requests.get(
        url_for('api.get_random', _external=True)
    )
    featured = response_random.json()

    response_recent = requests.get(
        url_for('api.get_recent', _external=True)
    )
    recent = response_recent.json()

    return render_template(
        'beta.html', 
        featured=featured, 
        recent=recent
    )

@web_bp.route("/all_cafes")
def show_all():
    response_all = requests.get(
        url_for('api.get_all', _external=True)
    )
    all_cafes = response_all.json()
    return render_template(
        'all.html', 
        all=all_cafes
    )


@web_bp.route("/add_cafe", methods=['GET', 'POST'])
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

@web_bp.route('/cafe/<int:cafe_id>', methods=['GET'])
def show_cafe(cafe_id):
    response_view = requests.get(
        url_for('api.view_by_id', cafe_id=cafe_id, _external=True)
    )
    cafe_selected = response_view.json()

    return render_template(
        'viewcafe.html',
        cafe_data=cafe_selected
    )