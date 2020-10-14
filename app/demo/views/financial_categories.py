import json
from flask import session, redirect, url_for, render_template, flash, request
from .blueprint import demo_blueprint
from app.models import Subdomain
from app.demo.forms import CategoriesForm


@demo_blueprint.route("/financial_categories", methods=["GET", "POST"])
def financial_categories():
    form = CategoriesForm(request.form)
    form.selected_features = session.get("selected_features", [])
    form.categories = json.loads(session.get("categories", "{}"))
    form.subdomain = Subdomain.query.get(session.get("subdomain", None))
    # ranges_for_feature = session.get("ranges_for_feature", {})
    if form.validate_on_submit():
        if form.submit.data:
            form.categories[form.category_name.data] = [
                k for k in request.form if request.form[k] == "on"
            ]
            session["categories"] = json.dumps(form.categories)
        if form.next.data:
            if not form.categories:
                flash("Need define at least one category", "danger")
                return render_template("categories.html", form=form)
            session["categories"] = json.dumps(form.categories)
            # {}
            return redirect(url_for("demo.financial_explan_summary"))
    elif form.is_submitted():
        flash("Invalid data", "warning")
    return render_template("financial_categories.html", form=form)
