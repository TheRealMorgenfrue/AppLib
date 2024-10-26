# Temp template to test arbitrarily nested configs - taken from early development of P5 project

from typing import Self


class ConfigTemplate(object):
    """Singleton that defines as configuration template for the project.
    Note: We added additional params/longer attribute accesses for clarity."""

    _instance = None

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._template = (
                cls._createTemplate()
            )  # Added field access for clariy - VS-code cares, Python doesn't
        return cls._instance

    def getTemplate(self) -> dict:
        return self._template

    @classmethod
    def _createTemplate(self) -> dict:
        return {
            "General": {
                "loglevel": "DEBUG",
                "UseCleaner": True,
                "UseFeatureSelector": True,
                "UseTransformer": True,
                "UseModelSelector": True,
                "UseModelTrainer": True,
                "UseModelTester": True,
                "UseModelEvaluator": True,
            },
            "DataPreprocessing": {
                "Cleaning": {
                    "DeleteNanColumns": True,
                    "DeleteNonfeatures": False,
                    "DeleteMissingValues": False,
                    "DeleteUndeterminedValue": False,
                    "RemoveFeaturelessRows": True,
                    "RFlRParams": 3,
                    "FillNan": True,
                    "ShowNan": True,
                    "CleanRegsDataset": True,
                    "CleanMålDataset": True,  #        These three options should be handled by the run-method in the cleaner.py file
                    "CleanOldDastaset": True,
                },
                "OutlierAnalysis": {
                    "OutlierRemovalMethod": "odin",  # None, odin, avf
                    "odinParams": {
                        "k": 30,
                        "T": 0,
                    },  # {number of neighbors, indegree threshold}
                    "avfParams": {"k": 10},  # {number of outliers to detect}
                },
                "Transformer": {
                    "OneHotEncode": "T",
                    "ImputationMethod": "KNN",  # None, Mode, KNN
                    "NearestNeighbors": 5,
                    "Normalisation": "minMax",  # None, minMax
                },
                "FeatureSelection": {
                    "_computeFeatureCorrelation": "",
                    "_chi2Independence": "",
                    "_fClassifIndependence": "",
                    "_mutualInfoClassif": "",
                    "genericUnivariateSelect": "",
                    "varianceThreshold": "",
                    "permutationFeatureImportance": "",
                    "permutation_importance": "",
                    "checkOverfitting": "",
                    "recursiveFeatureValidation": "",
                    "recursiveFeatureValidationWithCrossValidation": "",
                },
            },
            "ModelSelection": {
                "model": "Model.DECISION_TREE.name",
                "DecisionTree": {
                    "criterion": "entropy",  # type: Literal["gini", "entropy", "log_loss"]
                    "max_depth": None,  # type: int | None
                    "min_samples_split": 2,
                    "min_samples_leaf": 1,
                    "min_weight_fraction_leaf": 0,  # type: int | float
                    "max_features": None,  # type: int | None
                    "random_state": 42,  # type: int | None
                    "max_leaf_nodes": None,  # type: int | None
                    "min_impurity_decrease": 0.0,
                    "ccp_alpha": 0.0,
                },
                "RandomForest": {
                    "n_estimators": 100,
                    "bootstrap": True,
                    "oob_score": False,  # type: bool | Callable
                    "n_jobs": -1,
                    "random_state": 53,  # type: int | None
                    "max_samples": None,  # type: int | float | None
                },
            },
            "CrossValidationSelection": {
                "cross_validator": "CrossValidator.STRATIFIED_KFOLD.name",  # type: CrossValidator | None
                "StratifiedKFold": {
                    "n_splits": 5,
                    "shuffle": True,
                    "random_state": 177,  # type: int | None
                },
                "TimeSeriesSplit": {
                    "n_splits": 5,
                    "max_train_size": None,  # type: int | None
                    "test_size": None,  # type: int | None
                    "gap": 0,
                },
            },
            "ModelTraining": {"test3": ""},
            "ModelTesting": {"test4": ""},
            "ModelEvaluation": {"test5": ""},
        }
