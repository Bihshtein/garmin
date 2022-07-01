from abc import ABC, abstractmethod, ABCMeta
import pandas as pd


class LevelEvaluator(ABC):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_level(self, metrics: list):
        pass


class StrideLevelEvaluator(LevelEvaluator):
    def get_level(self, metrics: pd.DataFrame):
        if len(metrics[metrics['stride'] >= 150].index) > len(metrics.index)/2:
            return 1
        elif len(metrics[metrics['stride'] >= 100].index) > len(metrics.index)/2:
            return 2
        else:
            return 3


class CadenceLevelEvaluator(LevelEvaluator):
    def get_level(self, metrics: pd.DataFrame):
        if len(metrics[metrics['cadence'] >= 170].index) > len(metrics.index)/2:
            return 1
        elif len(metrics[metrics['cadence'] >= 160].index) > len(metrics.index)/2:
            return 2
        else:
            return 3


class HeartRateLevelEvaluator(LevelEvaluator):
    def get_level(self, metrics: pd.DataFrame):
        if len(metrics[metrics['R_HR'] <= 60].index) > len(metrics.index)/2:
            return 1
        elif len(metrics[metrics['R_HR'] <= 70 ].index) > len(metrics.index)/2:
            return 2
        else:
            return 3


class Vo2MaxLevelEvaluator(LevelEvaluator):
    def get_level(self, metrics: pd.DataFrame):
        if len(metrics[metrics['vo2max'] >= 60].index) > len(metrics.index)/2:
            return 1
        elif len(metrics[metrics['vo2max'] >= 50].index) > len(metrics.index)/2:
            return 2
        else:
            return 3
