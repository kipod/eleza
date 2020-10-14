import enum
from sqlalchemy import Enum
from app.database import db
from app.utils import ModelMixin


class Subdomain(db.Model, ModelMixin):
    """Subdomain entity"""

    __tablename__ = "subdomain"

    class Domain(enum.Enum):
        initial = "Initial"
        general = "General"
        healthcare = "Healthcare"
        financial = "Financial"
        education = "Education"
        manufactiring = "Manufacturing"
        legal = "Legal"

    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(Enum(Domain), default=Domain.initial)
    name = db.Column(db.String(64), unique=True, nullable=False)

    def __repr__(self):
        return "<Subdomain:{0} {1}>".format(self.domain.name, self.name)

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name}

    @staticmethod
    def columns():
        return ["ID", "DOMAIN", "NAME"]
