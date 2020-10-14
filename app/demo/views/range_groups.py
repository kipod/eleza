from flask import session, request, redirect, url_for, render_template, flash
from .blueprint import demo_blueprint
from app.models import Subdomain, Feature, CaseValue
from app.demo.forms import RangeGroupsForm


@demo_blueprint.route("/range_groups", methods=["GET", "POST"])
def range_groups():
    form = RangeGroupsForm(request.form)
    form.selected_features = session.get("selected_features", [])
    form.subdomain = Subdomain.query.get(session.get("subdomain", None))
    user_data_id = session["user_data_id"]
    form.feature.choices = [(v, v) for v in form.selected_features]
    form.ranges = {}
    ranges_for_feature = session.get("ranges_for_feature", {})
    Feature_Name_Age = "Age"
    for feature_name in form.selected_features:
        feature = Feature.query.filter(Feature.name == feature_name).first()
        all_values = [
            c.value
            for c in CaseValue.query.filter(CaseValue.user_data_id == user_data_id)
            .filter(CaseValue.feature == feature)
            .all()
        ]
        if feature_name == Feature_Name_Age:
            form.ranges[feature_name] = (
                int(min(all_values)),
                int(max(all_values)),
            )
        else:
            form.ranges[feature_name] = (
                round(min(all_values), 3),
                round(max(all_values), 3),
            )
    if form.validate_on_submit():
        if form.next.data:
            session["categories"] = "{}"
            return redirect(url_for("demo.categories"))
        try:
            min_val_of_range_from = float(form.ranges[form.feature.data][0])
            max_val_of_range_from = float(form.ranges[form.feature.data][1])
            if form.feature.data in ranges_for_feature:

                if form.feature.data == "Age":
                    if (
                        (
                            min_val_of_range_from > float(form.range_to.data)
                            or float(form.range_to.data) > max_val_of_range_from
                        )
                        or (float(form.range_from.data) < min_val_of_range_from)
                        or (float(form.range_from.data) > max_val_of_range_from)
                    ):
                        if float(form.range_from.data) < min_val_of_range_from or (
                            float(form.range_from.data) > max_val_of_range_from
                        ):
                            form.range_from.data = min_val_of_range_from
                        if (
                            min_val_of_range_from > float(form.range_to.data)
                            or float(form.range_to.data) > max_val_of_range_from
                        ):
                            form.range_to.data = max_val_of_range_from
                        ranges_for_feature[form.feature.data] += [
                            (
                                (
                                    int(float(form.range_from.data)),
                                    int(float(form.range_to.data)),
                                )
                            )
                        ]
                    else:
                        ranges_for_feature[form.feature.data] += [
                            (
                                (
                                    int(float(form.range_from.data)),
                                    int(float(form.range_to.data)),
                                )
                            )
                        ]

                elif (
                    (
                        min_val_of_range_from > float(form.range_to.data)
                        or float(form.range_to.data) > max_val_of_range_from
                    )
                    or (float(form.range_from.data) < min_val_of_range_from)
                    or (float(form.range_from.data) > max_val_of_range_from)
                ):
                    if float(form.range_from.data) < min_val_of_range_from or (
                        float(form.range_from.data) > max_val_of_range_from
                    ):
                        form.range_from.data = min_val_of_range_from
                    if (
                        min_val_of_range_from > float(form.range_to.data)
                        or float(form.range_to.data) > max_val_of_range_from
                    ):
                        form.range_to.data = max_val_of_range_from
                    ranges_for_feature[form.feature.data] += [
                        (float(form.range_from.data), float(form.range_to.data))
                    ]
                else:
                    ranges_for_feature[form.feature.data] += [
                        (float(form.range_from.data), float(form.range_to.data))
                    ]
            else:
                if form.feature.data == "Age":
                    if (
                        (
                            min_val_of_range_from > float(form.range_to.data)
                            or float(form.range_to.data) > max_val_of_range_from
                        )
                        or (float(form.range_from.data) < min_val_of_range_from)
                        or (float(form.range_from.data) > max_val_of_range_from)
                    ):
                        if float(form.range_from.data) < min_val_of_range_from or (
                            float(form.range_from.data) > max_val_of_range_from
                        ):
                            form.range_from.data = min_val_of_range_from
                        if (
                            min_val_of_range_from > float(form.range_to.data)
                            or float(form.range_to.data) > max_val_of_range_from
                        ):
                            form.range_to.data = max_val_of_range_from
                        ranges_for_feature[form.feature.data] = [
                            (
                                (
                                    int(float(form.range_from.data)),
                                    int(float(form.range_to.data)),
                                )
                            )
                        ]
                    else:
                        ranges_for_feature[form.feature.data] = [
                            (
                                (
                                    int(float(form.range_from.data)),
                                    int(float(form.range_to.data)),
                                )
                            )
                        ]

                elif (
                    (
                        min_val_of_range_from > float(form.range_to.data)
                        or float(form.range_to.data) > max_val_of_range_from
                    )
                    or (float(form.range_from.data) < min_val_of_range_from)
                    or (float(form.range_from.data) > max_val_of_range_from)
                ):
                    if float(form.range_from.data) < min_val_of_range_from or (
                        float(form.range_from.data) > max_val_of_range_from
                    ):
                        form.range_from.data = min_val_of_range_from
                    if (
                        min_val_of_range_from > float(form.range_to.data)
                        or float(form.range_to.data) > max_val_of_range_from
                    ):
                        form.range_to.data = max_val_of_range_from
                        ranges_for_feature[form.feature.data] = [
                            (float(form.range_from.data), float(form.range_to.data))
                        ]
                    else:
                        ranges_for_feature[form.feature.data] = [
                            (float(form.range_from.data), float(form.range_to.data))
                        ]
                else:
                    ranges_for_feature[form.feature.data] = [
                        (float(form.range_from.data), float(form.range_to.data))
                    ]

            session["ranges_for_feature"] = ranges_for_feature
        except ValueError:
            flash("Invalid data", "warning")
    elif form.is_submitted():
        flash("Invalid data", "warning")

    return render_template(
        "range_groups.html", form=form, ranges_for_feature=ranges_for_feature
    )
