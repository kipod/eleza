from .database import db


class ModelMixin(object):

    def save(self, do_commit=True):
        # Save this model to the database.
        db.session.add(self)
        if do_commit:
            db.session.commit()
        return self


# Add your own utility classes and functions here.
