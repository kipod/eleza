from ..database import db
from app.utils import ModelMixin


class Feature(db.Model, ModelMixin):
    """Feature entity"""
    __tablename__ = "feature"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    short_name = db.Column(db.String(64), unique=True, nullable=False)

    def __repr__(self):
        return '<Feature %r>' % self.name

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name, }

    @staticmethod
    def columns():
        return ["ID", "Name"]
