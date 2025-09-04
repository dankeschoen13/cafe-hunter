from flask import Blueprint, request, render_template, url_for
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