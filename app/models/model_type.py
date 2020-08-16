from ..database import db
from app.utils import ModelMixin


class ModelType(db.Model, ModelMixin):
    """ModelType entity"""
    __tablename__ = "model_type"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)

    def __repr__(self):
        return '<ModelType %r>' % self.name

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name}

    @staticmethod
    def columns():
        return ["ID", "NAME"]
