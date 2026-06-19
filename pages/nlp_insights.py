import streamlit as st

def show_nlp_insights(df):

    st.markdown("""
    <div class='page-title'>NLP Insights</div>
    <div class='page-subtitle'>
        Text mining and keyword analysis
    </div>
    """, unsafe_allow_html=True)

    st.info(
        "NLP model is under development."
    )

    st.markdown("""
    ### Planned Features

    - Word Cloud
    - Top Keywords
    - Topic Detection
    - Objection Classification
    - Sentiment Prediction
    """)