import enum
from sqlalchemy import Enum
from app.database import db
from app.utils import ModelMixin


class Subdomain(db.Model, ModelMixin):
    """Subdomain entity"""

    __tablename__ = "subdomain"

    class Type(enum.Enum):
        healthcare = "Healthcare"
        financial = "Financial"

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(Enum(Type), default=Type.healthcare)
    name = db.Column(db.String(64), unique=True, nullable=False)

    def __repr__(self):
        return "<Subdomain:{0} {1}>".format(self.type.name, self.name)

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name}

    @staticmethod
    def columns():
        return ["ID", "TYPE", "NAME"]
