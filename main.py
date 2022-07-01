import streamlit as st
import io
from level_evaluator import *
from notes import *
from metrics_manager import MetricsManager
st.set_page_config(layout="wide")


def run_website():
    st.header('Stride and oxygen insights for long distance runners')
    file = st.file_uploader("Export all garmin data zip (https://support.garmin.com/en-US/?faq=W1TvTPW8JZ6LfJSfK512Q8)")
    if file is not None:
        display_zipped_data(io.BytesIO(file.getvalue()))
    barefoot = 'Barefoot sample  data'
    semi_barefoot = 'Semi-barefoot sample data'
    shoes = 'Shoes sample data'
    option = st.selectbox(
        'Pick a sample data option for an impression on the insights',
        (barefoot, semi_barefoot, shoes))

    if option == barefoot:
        display_zipped_data('alex_barefoot.zip')

    elif option == semi_barefoot:
        display_zipped_data('alex_semi_barefoot.zip')

    elif option == shoes:
        display_zipped_data('shoes.zip')


def display_zipped_data(file):
    st.subheader('Cadence vs Stride and Vo2Max vs Resting heart rate trends')
    metrics_manager = MetricsManager(file)
    st.line_chart(metrics_manager.display_metrics)

    st.subheader('Monthly summarized stats')
    st.dataframe(metrics_manager.summarized_metrics)

    cadence_level = CadenceLevelEvaluator().get_level(metrics_manager.summarized_metrics)
    stride_level = StrideLevelEvaluator().get_level(metrics_manager.summarized_metrics)
    heart_rate_level = HeartRateLevelEvaluator().get_level(metrics_manager.summarized_metrics)
    vo2max_level = Vo2MaxLevelEvaluator().get_level(metrics_manager.summarized_metrics)

    st.subheader('Cadence insights')
    st.text(cadence_level_notes[cadence_level])

    st.subheader('Stride Insights')
    st.text(stride_level_notes[cadence_level][stride_level])

    st.subheader('Resting Heart Rate Insights')
    st.text(heart_rate_level_notes[heart_rate_level])

    st.subheader('Vo2Max Insights')
    st.text(vo2max_level_notes[vo2max_level])


if __name__ == '__main__':
    run_website()