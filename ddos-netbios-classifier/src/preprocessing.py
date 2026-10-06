import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class InfinityMaxImputer(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        X = X.copy(); self.feature_names_in_ = X.columns.tolist(); self.fill_values_ = {}
        for col in self.feature_names_in_:
            v = pd.to_numeric(X[col], errors='coerce'); finite = v[np.isfinite(v)]
            self.fill_values_[col] = float(finite.max()) if len(finite) else 0.0
        return self

    def transform(self, X):
        X = X.copy()
        for col, val in self.fill_values_.items():
            if col in X.columns: X[col] = X[col].replace([np.inf, -np.inf], val)
        return X

    def get_feature_names_out(self, input_features=None):
        return np.asarray(self.feature_names_in_, dtype=object)


class CorrelationFilter(BaseEstimator, TransformerMixin):
    def __init__(self, threshold=0.95): self.threshold = threshold

    def fit(self, X, y=None):
        X = X.copy(); self.feature_names_in_ = X.columns.tolist(); corr = X.corr().abs()
        upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
        self.features_to_drop_ = [col for col in upper.columns if any(upper[col] > self.threshold)]
        self.feature_names_out_ = [col for col in self.feature_names_in_ if col not in self.features_to_drop_]
        return self

    def transform(self, X): return X.copy().drop(columns=self.features_to_drop_, errors='ignore')

    def get_feature_names_out(self, input_features=None): return np.asarray(self.feature_names_out_, dtype=object)
