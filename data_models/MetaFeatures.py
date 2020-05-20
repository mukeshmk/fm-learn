from app import db, ma
from constants import TABLE_META_FEATURES


# Meta Feature Class/Model
class MetaFeature(db.Model):
    __tablename__ = TABLE_META_FEATURES
    id = db.Column(db.Integer, primary_key=True)
    metric_id = db.Column(db.Integer, db.ForeignKey('metric.id'), nullable=False)
    feat_name = db.Column(db.String(200))
    feat_value = db.Column(db.String(200))

    def __init__(self, metric_id, feat_name, feat_value):
        self.metric_id = metric_id
        self.feat_name = feat_name
        self.feat_value = feat_value


# Meta Feature Schema
class MetaFeatureSchema(ma.Schema):
    class Meta:
        fields = ('id', 'metric_id', 'feat_name', 'feat_value')


# Init schema
meta_feature_schema = MetaFeatureSchema()
meta_features_schema = MetaFeatureSchema(many=True)
