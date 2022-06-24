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
    merged_metrics = running_metrics.merge(user_metrics, on='date', how='left')
    metrics_to_display = \
        ['date', 'restingHeartRate', 'vO2MaxValue', 'avgStrideLengthRolling', 'avgDoubleCadenceRolling']
    display_metrics = merged_metrics[metrics_to_display] \
        .rename(columns={'date': 'index',
                         'restingHeartRate' : 'R_HR',
                         'vO2MaxValue' : 'V02Max',
                         'avgStrideLengthRolling' : 'Stride',
                         'avgDoubleCadenceRolling' : 'Cadence'
                         })\
        .set_index('index') \
        .dropna()
    st.subheader('Cadence vs Stride and Vo2Max vs Resting heart rate trends')
    st.line_chart(display_metrics)

    summarized = merged_metrics\
        .assign(
            month_year=lambda d: d.date.astype('datetime64[ns]').dt.month.astype(str) + '-' +
                                 d.date.astype('datetime64[ns]').dt.year.astype(str),
            monthly_average_distance=lambda d: d.groupby(by=d.month_year)['distance'].transform('mean')/100/100,
            monthly_average_stride= lambda d: d.groupby(by=d.month_year)['avgStrideLength'].transform('mean'),
            monthly_average_cadence = lambda d: d.groupby(by=d.month_year)['avgDoubleCadence'].transform('mean'),
            monthly_average_vo2max = lambda d: d.groupby(by=d.month_year)['vO2MaxValue'].transform('mean'),
            monthly_average_resting_heart_rate = lambda d: d.groupby(by=d.month_year)['restingHeartRate'].transform('mean')) \
            .drop_duplicates(subset=['month_year'])\
        .set_index('month_year') \
        .sort_values(by='date')\
        [['monthly_average_distance', 'monthly_average_stride', 'monthly_average_cadence',
          'monthly_average_vo2max', 'monthly_average_resting_heart_rate']].\
        fillna(0).astype(int)

    st.subheader('Monthly summarized stats')

    st.table(summarized)

    st.subheader('Insights')

    st.caption('1. Cadence')
    if len(summarized[summarized['monthly_average_cadence'] >= 170].index) == len(summarized.index):
        st.text('Brilliant! You got top cadence, keep it up!')
        cadence_score = 1
    elif len(summarized[summarized['monthly_average_cadence'] >= 160].index) == len(summarized.index):
        st.text('Your cadence can and should be improved,'
                ' try taking smaller steps or taking off your shoes and go above 170 steps per minute')
        cadence_score = 2
    else:
        st.text('Your cadence has significant room for improvement, '
                'try to taking smaller steps and go above 160 steps per minute')
        cadence_score = 3

    st.caption('Stride Length')
    if cadence_score == 1:
        st.text('It is time to work on your stride, '
                'try more interval training but do not go overboard! '
                'More than a few centimeters per month can get you injured!')
    elif len(summarized[summarized['monthly_average_stride'] >= 100].index) == len(summarized.index):
        st.text('Your stride is too long! First make sure you can perform at 170 and above cadence!')
    else:
        st.text('Focus on your cadence, keep decreasing your stride if needed')
    st.caption('Resting Heart Rate')
    if len(summarized[summarized['monthly_average_resting_heart_rate'] <= 70].index) == len(summarized.index):
        st.text('You are in a great aerobic shape, keep it up!')
        aerobic_score = 1
    else:
        st.text('Try increasing your monthly distance to help further improve your resting heart rate')
        aerobic_score = 2
    st.caption('Vo2Max')
    if aerobic_score == 1 and len(summarized[summarized['monthly_average_vo2max'] <= 50].index) > 0:
        st.text('To improve Vo2Max you might have to improve the technique or lower your weight even if it is muscle')
    else:
        st.text('With lower heart rate and better technique Vo2Max will increase')


if __name__ == '__main__':
    run_website()