from app import db, ma
from data_models.Params import ParamSchema
from data_models.MetaFeatures import MetaFeatureSchema
from constants import TABLE_METRIC, CLASS_PARAM, CLASS_META_FEATURE

# Metric Class/Model
class Metric(db.Model):
    __tablename__ = TABLE_METRIC
    id = db.Column(db.Integer, primary_key=True)
    algorithm_name = db.Column(db.String(200))
    dataset_hash = db.Column(db.Text)
    metric_name = db.Column(db.String(200))
    metric_value = db.Column(db.Float)
    target_type = db.Column(db.String(200))
    params = db.relationship(CLASS_PARAM, cascade = "all, delete", backref=TABLE_METRIC, lazy=True)
    meta_features = db.relationship(CLASS_META_FEATURE, cascade = "all, delete", backref=TABLE_METRIC, lazy=True)

    def __init__(self, algorithm_name, dataset_hash, metric_name, metric_value, target_type):
        self.algorithm_name = algorithm_name
        self.dataset_hash = dataset_hash
        self.metric_name = metric_name
        self.metric_value = metric_value
        self.target_type = target_type


# Metric Schema
class MetricSchema(ma.Schema):
    params = ma.Nested(ParamSchema, many=True)
    meta_features = ma.Nested(MetaFeatureSchema, many=True)
    class Meta:
        fields = ('id', 'algorithm_name', 'dataset_hash', 'metric_name', 'metric_value', 'target_type', 'params', 'meta_features')
        include_fk = True


# Init schema
metric_schema = MetricSchema()
metrics_schema = MetricSchema(many=True)
