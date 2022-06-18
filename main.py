import streamlit as st
import io
import zipfile
import os
from metric_builders import MetricsBuilders

st.set_page_config(layout="wide")


def run_website():
    st.title('Stride and oxygen insights for long distance runners')
    file = st.file_uploader("Export all garmin data zip (https://support.garmin.com/en-US/?faq=W1TvTPW8JZ6LfJSfK512Q8)")
    if file is not None:
        display_zipped_data(io.BytesIO(file.getvalue()))

    if st.button('Display barefoot sample  data'):
        display_zipped_data('alex_barefoot.zip')

    if st.button('Display semi-barefoot sample data'):
        display_zipped_data('alex_semi_barefoot.zip')


def display_zipped_data(file):
    local_folder_path = os.path.join(os.getcwd(), 'data')

    with zipfile.ZipFile(file) as zip_ref:
        zip_ref.extractall(local_folder_path)
    user_metrics = MetricsBuilders.build_user_metrics(local_folder_path)
    running_metrics = MetricsBuilders.build_running_metrics(local_folder_path)
    metrics_to_display = \
        ['date', 'restingHeartRate', 'vO2MaxValue', 'avgStrideLengthRolling', 'avgDoubleCadenceRolling']
    display_metrics = running_metrics.merge(user_metrics, on='date', how='left')[metrics_to_display] \
        .rename(columns={'date': 'index',
                         'restingHeartRate' : 'R_HR',
                         'vO2MaxValue' : 'V02Max',
                         'avgStrideLengthRolling' : 'Stride',
                         'avgDoubleCadenceRolling' : 'Cadence'
                         })\
        .set_index('index') \
        .dropna()
    st.line_chart(display_metrics)


if __name__ == '__main__':
    run_website()