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
    diagnosis_id = db.Column(db.Integer, db.ForeignKey("diagnosis.id"))
    model_type_id = db.Column(db.Integer, db.ForeignKey("model_type.id"))
    feature_id = db.Column(db.Integer, db.ForeignKey("feature.id"))
    diagnosis = relationship("Diagnosis")
    model_type = relationship("ModelType")
    feature = relationship("Feature")



    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.сase, "value": self.value}

    @staticmethod
    def columns():
        return ["ID", "CASE", "VALUE"]