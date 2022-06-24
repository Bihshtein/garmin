import pandas as pd
import glob
import json
import os
import shutil


class MetricsBuilders:

    @staticmethod
    def build_user_metrics(local_folder_path):
        path = os.path.join(local_folder_path, 'DI_CONNECT/DI-Connect-User', 'UDSFile*.json')
        files = glob.glob(path)
        dfs = [pd.read_json(file) for file in files]
        return pd.concat(dfs).dropna(subset=['calendarDate']) \
            .assign(vigorousIntensityMinutesRolling=lambda d: d['vigorousIntensityMinutes'].rolling(1).mean(),
                    moderateIntensityMinutesRolling=lambda d: d['moderateIntensityMinutes'].rolling(1).mean(),
                    date=lambda d: d['calendarDate'].apply(lambda cell: pd.to_datetime(cell['date']).date()))\
            .sort_values(by='date')

    @staticmethod
    def build_running_metrics(local_folder_path):
        path = os.path.join(local_folder_path, 'DI_CONNECT/DI-Connect-Fitness', '*summarizedActivities.json')
        files = glob.glob(path)
        dfs = [pd.DataFrame.from_records(json.load(open(file))[0]['summarizedActivitiesExport']) for file in files]
        shutil.rmtree(local_folder_path)

        df = pd.concat(dfs)\
            .query("name == 'Running' & avgDoubleCadence > 145")\
            .assign(avgStrideLengthRolling=lambda d: d['avgStrideLength'].rolling(1).mean(),
                    avgDoubleCadenceRolling=lambda d: d['avgDoubleCadence'].rolling(1).mean(),
                    date=lambda d: pd.to_datetime(d['beginTimestamp'], unit='ms').dt.date)

        return df
