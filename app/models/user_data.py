from datetime import datetime
from app.database import db
from app.utils import ModelMixin


class UserData(db.Model, ModelMixin):
    """UserData entity"""

    __tablename__ = "user_data"

    id = db.Column(db.Integer, primary_key=True)
    created_date = db.Column(db.DateTime, default=datetime.now)
