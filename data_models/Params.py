from app import db, ma
from constants import TABLE_PARAM


# Product Class/Model
class Params(db.Model):
    __tablename__ = TABLE_PARAM
    id = db.Column(db.Integer, primary_key=True)
    metric_id = db.Column(db.Integer, db.ForeignKey('metric.id'), nullable=False)
    param_name = db.Column(db.String(200))
    param_value = db.Column(db.String(200))

    def __init__(self, metric_id, param_name, param_value):
        self.metric_id = metric_id
        self.param_name = param_name
        self.param_value = param_value


# Product Schema
class ParamSchema(ma.Schema):
    class Meta:
        fields = ('id', 'metric_id', 'param_name', 'param_value')


# Init schema
param_schema = ParamSchema()
params_schema = ParamSchema(many=True)
