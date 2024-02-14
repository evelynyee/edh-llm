"""
App for displaying results.
"""

import numpy as np
import streamlit as st
import pandas as pd
import pickle
import re
import os

# formatting constants
SPECIAL_CHARS = ['*','#','$','_','>','`',':']

# data processing constants
RESULTS_PATH = os.path.abspath(os.path.join('..','data'))

# Load data
@st.cache_data
def load_data(path):
    # TODO
    return pd.read_csv(path, dtype=str,na_values=[''],keep_default_na=False, index_col=False).dropna(how='all')

def clean_text (text): # format text for compatible with markdown
    text = text.strip()
    for special in SPECIAL_CHARS: # escape special markdown characters
        text = text.replace(special, '\\'+special)
    text = text.replace('\n','\n\n') # make sure single newlines also break the text
    return text

def dataset_selector():
    # TODO: UPDATE THIS
    # Dataset selector
    datasets = [dataset for dataset in os.listdir(RESULTS_PATH)
                if len(os.listdir(os.path.join(RESULTS_PATH,dataset)))>0] # don't list empty datasets
    st.sidebar.selectbox(
            "Choose a dataset",
            datasets,
            key='dataset general'
        )
    files = [file for file in os.listdir(os.path.join(RESULTS_PATH,st.session_state['dataset general']))
             if 'summary' not in file
             and 'adjusted' in file
             and 'annotation' not in file
             and file[-3:] == 'csv']
    st.sidebar.selectbox(
            "Choose a data file",
            files,
            key='dataset name',
            on_change=new_dataset #get_question_idx,
            # kwargs={'annotations_path':os.path.join(RESULTS_PATH,st.session_state['dataset general'],'_annotations.'.join(st.session_state['dataset name'].split('.'))),'new_dataset':True}
        )
    data_path = os.path.join(RESULTS_PATH,st.session_state['dataset general'],st.session_state['dataset name'])
    return data_path

def dashboard_page():
    # Dataset selector
    data_path = dataset_selector()

    # page content
    st.title("Dashboard Page")

# Main app
def main():
    # Title
    page = None
    st.set_page_config(layout="wide")
    dashboard_page()


# Run the app
if __name__ == "__main__":
    main()
