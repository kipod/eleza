from ..database import db
from app.utils import ModelMixin
from sqlalchemy.orm import relationship


class CaseValue(db.Model, ModelMixin):
    """CaseValue entity"""

    __tablename__ = "case_value"

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, nullable=False)
    value = db.Column(db.Float)
    explainer = db.Column(db.Float)
    prediction = db.Column(db.Float)
    subdomain_id = db.Column(db.Integer, db.ForeignKey("subdomain.id"), nullable=False)
    model_type_id = db.Column(db.Integer, db.ForeignKey("model_type.id"), nullable=False)
    feature_id = db.Column(db.Integer, db.ForeignKey("feature.id"), nullable=False)
    user_data_id = db.Column(db.Integer, db.ForeignKey("user_data.id"), nullable=False)
    subdomain = relationship("Subdomain")
    model_type = relationship("ModelType")
    feature = relationship("Feature")
    user_data = relationship("UserData")

    def __repr__(self):
        return "<Val({}) case_id:{} val:{} ex:{} name:{}>".format(
            self.id, self.case_id, self.value, self.explainer, self.feature.short_name
        )

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.сase, "value": self.value}

    @staticmethod
    def columns():
        return ["ID", "CASE", "VALUE"]
