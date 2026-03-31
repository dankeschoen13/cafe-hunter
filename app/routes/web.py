import logging
from flask import Blueprint, render_template, url_for, redirect, flash, request
from flask_login import login_required, current_user
from app.forms import AddForm
from app.utils import admin_only, to_embed_url
from app.constants import Alerts, Errors, Actions
from app.services import CafeService


web_bp = Blueprint("web", __name__)

@web_bp.route("/all-cafes")
def cafe_index():
    all_cafes = CafeService.fetch_all()

    return render_template(
        'main/all.html',
        all=all_cafes
    )


@web_bp.route("/")
def home():
    recent_cafes = CafeService.fetch_recent()

    if not recent_cafes:
        return redirect(url_for('web.add_new_cafe'))

    featured_cafe = CafeService.fetch_featured()

    if not featured_cafe:
        featured_cafe = [CafeService.fetch_random()]
        logging.info(Alerts.RANDOM_API_CALLED)

    return render_template(
        'home.html',
        recent=recent_cafes,
        featured=featured_cafe
    )


@web_bp.route('/show-cafe/id=<int:cafe_id>', methods=['GET'])
def show(cafe_id):
    cafe_selected = CafeService.fetch_by_id(cafe_id)
    embed_url = to_embed_url(cafe_selected.map_url)

    return render_template(
        'main/view.html',
        cafe_data=cafe_selected,
        embed_url=embed_url
    )


@web_bp.route('/search', methods=['GET'])
def search():
    return render_template('main/search.html')


@web_bp.route('/rate-cafe/id=<int:cafe_id>', methods=['POST'])
@login_required
def rate_cafe(cafe_id):
    rating = request.form.get('rating', type=int)

    if not rating or rating not in range(1, 6):
        flash("Invalid rating submitted.", 'danger')
        return redirect(url_for("web.show", cafe_id=cafe_id))

    try:
        cafe_rated = CafeService.rate(cafe_id, rating, current_user)

        if not cafe_rated:
            flash(Errors.ID_NOT_FOUND, 'danger')
            return redirect(url_for("web.cafe_index"))

    except ValueError as e:
        flash(str(e), category='danger')
        return redirect(url_for("web.show", cafe_id=cafe_id))

    flash(Alerts.CAFE_RATED, 'success')
    return redirect(url_for("web.show", cafe_id=cafe_id))


@web_bp.route("/add-cafe", methods=['GET', 'POST'])
@admin_only
def add():
    form = AddForm()
    
    if form.validate_on_submit():
        
        clean_data = form.data
        clean_data.pop('csrf_token', None)

        try:
            CafeService.create(clean_data)

        except ValueError as e:
            flash(str(e), 'danger')
            return render_template(
                'dashboard/modify.html',
                form=form,
                action=Actions.ADD_NEW_CAFE
            )

        flash(Alerts.CAFE_ADDED, 'success')
        return redirect(url_for("web.cafe_index"))

    return render_template(
        'dashboard/modify.html',
        form=form,
        action=Actions.ADD_NEW_CAFE
    )


@web_bp.route('/edit-cafe/id=<int:cafe_id>', methods=['GET', 'POST'])
@admin_only
def edit(cafe_id):

    cafe_to_edit = CafeService.fetch_by_id(cafe_id)

    if not cafe_to_edit:
        flash(Errors.ID_NOT_FOUND, 'danger')
        return redirect(url_for('web.cafe_index'))

    form = AddForm(obj=cafe_to_edit)

    if form.validate_on_submit():

        updated_data = form.data
        updated_data.pop('csrf_token', None)

        try:
            CafeService.update(updated_data, cafe_id)

        except ValueError as e:
            flash(str(e), category='danger')
            return render_template(
                'dashboard/modify.html',
                form=form,
                action=Actions.EDITING_CAFE
            )

        flash(Alerts.CAFE_UPDATED, 'success')
        return redirect(
            url_for('web.show', cafe_id=cafe_id)
        )

    return render_template(
        'dashboard/modify.html',
        form=form,
        action=Actions.EDITING_CAFE
    )


@web_bp.post('/delete-cafe/id=<int:cafe_id>')
@admin_only
def delete(cafe_id):
    cafe_deleted = CafeService.soft_delete(cafe_id)

    if not cafe_deleted:
        flash(Errors.ID_NOT_FOUND, 'danger')

    flash(Alerts.CAFE_DELETED, 'success')
    return redirect(url_for("web.cafe_index"))