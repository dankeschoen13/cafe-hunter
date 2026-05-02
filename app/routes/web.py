import logging
from typing import Any
from flask import Blueprint, render_template, url_for, redirect, flash, request, current_app, abort, g
from flask_login import login_required, current_user
from app.forms import AddForm
from app.utils import access_required, to_embed_url
from app.constants import Alerts, Errors, Actions
from app.services import CafeService


web_bp = Blueprint("web", __name__)


@web_bp.get("/all-cafes")
def cafe_index():
    all_cafes = CafeService.fetch_all()

    return render_template(
        'main/all-cafes.html',
        all=all_cafes
    )


@web_bp.get('/')
def home():
    recent_cafes = CafeService.fetch_recent()

    if not recent_cafes:
        return redirect(url_for('web.cafe_index'))

    featured_cafe = CafeService.fetch_featured()

    if not featured_cafe:
        featured_cafe = [CafeService.fetch_random()]
        logging.info(Alerts.RANDOM_API_CALLED)

    return render_template(
        'home.html',
        recent=recent_cafes,
        featured=featured_cafe
    )


@web_bp.get('/show-cafe/id=<int:cafe_id>')
def show(cafe_id):
    cafe_selected = CafeService.fetch_by_id(cafe_id)

    recent_three = CafeService.fetch_recent(
        limit=3, excluded_id=cafe_id
    )

    if not cafe_selected:
        return redirect(url_for('web.cafe_index'))

    embed_url = to_embed_url(cafe_selected.map_url)

    return render_template(
        'main/view-cafe.html',
        cafe_data=cafe_selected,
        recent=recent_three,
        embed_url=embed_url
    )


@web_bp.get('/search')
def search():
    bool_keys = ['wifi', 'sockets', 'calls', 'toilet']

    params: dict[str, Any] = {
        k: (v.lower() == 'true' if k in bool_keys else v)
        for k, v in request.args.items()
    }
    params['page'] = int((params.get('page', '1')))
    params |= {
        'per_page': current_app.config['SR_PER_PAGE']
    }

    no_matches = False
    results = CafeService.search(**params) 

    is_actively_searching = params.get('q') or any(params.get(k) for k in bool_keys)

    if len(results) == 0 and is_actively_searching and params['page'] == 1:
        no_matches = True
        results = CafeService.search(page=1, per_page=3)

    if request.headers.get('X-Requested-With') == 'Fetch':
        return render_template(
            'components/search-result.html',
            cafes=results,
            no_matches=no_matches
        )

    return render_template(
        'main/search-page.html',
        cafes=results,
        no_matches=no_matches
    )


@web_bp.post('/rate-cafe/id=<int:cafe_id>')
@login_required
def rate_cafe(cafe_id):
    rating = request.form.get('rating', type=int)

    if not rating or rating not in range(1, 6):
        flash(Errors.INVALID_RATING, 'danger')
        return redirect(
            url_for("web.show", cafe_id=cafe_id)
        )

    try:
        cafe_rated = CafeService.rate(
            cafe_id, rating, current_user
        )

        if not cafe_rated:
            flash(Errors.ID_NOT_FOUND, 'danger')
            return redirect(url_for("web.cafe_index"))

    except ValueError as e:
        flash(str(e), category='danger')
        return redirect(url_for("web.show", cafe_id=cafe_id))

    flash(Alerts.CAFE_RATED, 'success')
    return redirect(url_for("web.show", cafe_id=cafe_id))


@web_bp.route("/add-cafe", methods=['GET', 'POST'])
@access_required
def add():
    form = AddForm()
    
    if form.validate_on_submit():
        
        clean_data = form.data
        clean_data.pop('csrf_token', None)

        author = current_user

        try:
            CafeService.create(clean_data, author)

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
@access_required
def edit(cafe_id):
    cafe_to_edit = g.current_cafe

    if not cafe_to_edit:
        flash(Errors.ID_NOT_FOUND, 'danger')
        return redirect(url_for('web.cafe_index'))

    form = AddForm(obj=cafe_to_edit)

    if form.validate_on_submit():

        updated_data = form.data
        updated_data.pop('csrf_token', None)

        try:
            CafeService.update(updated_data, cafe_id, current_user)

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
@access_required
def delete(cafe_id):
    cafe_deleted = CafeService.soft_delete(cafe_id)

    if not cafe_deleted:
        flash(Errors.ID_NOT_FOUND, 'danger')

    flash(Alerts.CAFE_DELETED, 'success')
    return redirect(url_for("web.cafe_index"))


@web_bp.get('/report-changes')
def report_changes():
    return render_template('main/under-construction.html')


@web_bp.get('/about-us')
def about_us():
    return render_template('main/under-construction.html')


@web_bp.get('/best-cafes')
def best_cafes():
    return render_template('main/under-construction.html')


@web_bp.errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html')