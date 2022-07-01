import zipfile
import os
from metric_builders import MetricsBuilders


class MetricsManager:
    def __init__(self, file):
        merged_metrics = MetricsManager.get_merged_metrics(file)
        self.display_metrics = MetricsManager.build_display_metrics(merged_metrics)
        self.summarized_metrics = MetricsManager.build_summarized_metrics(merged_metrics)

    @staticmethod
    def get_merged_metrics(file):
        local_folder_path = os.path.join(os.getcwd(), 'data')

        with zipfile.ZipFile(file) as zip_ref:
            zip_ref.extractall(local_folder_path)
        user_metrics = MetricsBuilders.build_user_metrics(local_folder_path)
        running_metrics = MetricsBuilders.build_running_metrics(local_folder_path)
        return running_metrics.merge(user_metrics, on='date', how='left')

    @staticmethod
    def build_display_metrics(merged_metrics):

        metrics_to_display = \
            ['date', 'restingHeartRate', 'vO2MaxValue', 'avgStrideLengthRolling', 'avgDoubleCadenceRolling']
        return merged_metrics[metrics_to_display] \
            .rename(columns={'date': 'index',
                             'restingHeartRate' : 'R_HR',
                             'vO2MaxValue' : 'V02Max',
                             'avgStrideLengthRolling' : 'Stride',
                             'avgDoubleCadenceRolling' : 'Cadence'
                             })\
            .set_index('index') \
            .dropna()

    @staticmethod
    def build_summarized_metrics(merged_metrics):
        return merged_metrics\
            .assign(
                month_year=lambda d: d.date.astype('datetime64[ns]').dt.month.astype(str) + '-' +
                                     d.date.astype('datetime64[ns]').dt.year.astype(str),
                distance=lambda d: d.groupby(by=d.month_year)['distance'].transform('sum')/100/1000,
                stride=lambda d: d.groupby(by=d.month_year)['avgStrideLength'].transform('mean'),
                cadence=lambda d: d.groupby(by=d.month_year)['avgDoubleCadence'].transform('mean'),
                vo2max=lambda d: d.groupby(by=d.month_year)['vO2MaxValue'].transform('mean'),
                R_HR=lambda d: d.groupby(by=d.month_year)['restingHeartRate'].transform('mean')) \
                .drop_duplicates(subset=['month_year'])\
            .set_index('month_year') \
            .sort_values(by='date')\
            [['distance', 'stride', 'cadence', 'vo2max', 'R_HR']].\
            fillna(0).astype(int)