#!/user/bin/env python
import click
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import redirect, url_for, request

from app import create_app, models, forms
from app.database import db, db_fill_data
from app.models import User, Feature, Subdomain, ModelType

app = create_app()
# set optional bootswatch theme
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
admin = Admin(app, name='Eleza Admin', template_mode='bootstrap3')


class ElezaModelView(ModelView):

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('auth.login', next=request.url))


admin.add_view(ElezaModelView(User, db.session))
admin.add_view(ElezaModelView(Feature, db.session))
admin.add_view(ElezaModelView(Subdomain, db.session))
admin.add_view(ElezaModelView(ModelType, db.session))


# flask cli context setup


@app.shell_context_processor
def get_context():
    """Objects exposed here will be automatically available from the shell."""
    return dict(app=app, db=db, models=models, forms=forms)


@app.cli.command()
def create_db():
    """Create the configured database."""
    db.create_all()
    db_fill_data()


@app.cli.command()
@click.confirmation_option(prompt="Drop all database tables?")
def drop_db():
    """Drop the current database."""
    db.drop_all()


if __name__ == "__main__":
    app.run()
