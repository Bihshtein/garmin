import streamlit as st
import pandas
import glob
import json
import io
import os
import shutil

st.set_page_config(layout="wide")
st.title('GARMIN insights for long distance runners')
file = st.file_uploader("Please choose a file" )
if file is not None:
    bytes_data = file.getvalue()
    import zipfile
    local_path= os.path.join(os.getcwd(), 'data')
    with zipfile.ZipFile(io.BytesIO(bytes_data)) as zip_ref:
        zip_ref.extractall(local_path)

    dfs = []
    folders = ['.']
    all_files = []
    for folder in folders:
        path = os.path.join(local_path, 'DI_CONNECT/DI-Connect-User' , 'UDSFile*.json')

        all_files = all_files + glob.glob(path)
    for file in all_files:
        dfs.append(pandas.read_json(file))
    df = pandas.concat(dfs).dropna(subset=['calendarDate'])

    df['vigorousIntensityMinutesRolling'] = df['vigorousIntensityMinutes'].rolling(5).mean()
    df['moderateIntensityMinutesRolling'] = df['moderateIntensityMinutes'].rolling(5).mean()
    df = df.assign(date=df['calendarDate'].apply(lambda cell: pandas.to_datetime(cell['date']).date())).sort_values(by='date')
    health_data_df = df
    files = []
    for folder in folders:
        path = os.path.join(local_path, 'DI_CONNECT/DI-Connect-Fitness' , '*summarizedActivities.json')
        files = files + glob.glob(path)
    dfs = []
    for file in files:
        _json = json.load(open(file))
        dfs.append(pandas.DataFrame.from_records(_json[0]['summarizedActivitiesExport']))
    shutil.rmtree(local_path)

    df = pandas.concat(dfs)
    df = df[df['name'] == 'Running']
    df = df[df['avgDoubleCadence']>145]
    df['avgStrideLengthRolling']=df['avgStrideLength'].rolling(3).mean()
    df['avgDoubleCadenceRolling']=df['avgDoubleCadence'].rolling(3).mean()
    df['date'] = pandas.to_datetime(df['beginTimestamp'], unit='ms').dt.date
    df = df.merge(health_data_df, on='date', how='left')
    x = df['date']

    df = df[['date', 'avgStrideLengthRolling','avgDoubleCadenceRolling']]\
            .rename(columns={'date':'index'}).set_index('index')
    st.line_chart(data=df, use_container_width=True)

