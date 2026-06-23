import streamlit as st
import pandas as pd
import plotly.express as px

from utils.nlp_enrichment import NLP_META_KEY


def show_data_explorer(df):

    st.markdown("""
    <div class='page-title'>
    Data Explorer
    </div>
    <div class='page-subtitle'>
    Browse raw records with NLP-enriched sentiment and subclass fields
    </div>
    """, unsafe_allow_html=True)

    working_df = df.copy()

    filter_col1, filter_col2, filter_col3 = st.columns(3)

    with filter_col1:
        if "Sentiment" in working_df.columns:
            sentiment_filter = st.multiselect(
                "Sentiment",
                options=sorted(working_df["Sentiment"].dropna().unique()),
                default=sorted(working_df["Sentiment"].dropna().unique()),
            )
        else:
            sentiment_filter = []

    with filter_col2:
        if "Subclass" in working_df.columns:
            subclass_filter = st.multiselect(
                "Subclass",
                options=sorted(working_df["Subclass"].dropna().unique()),
                default=sorted(working_df["Subclass"].dropna().unique()),
            )
        else:
            subclass_filter = []

    with filter_col3:
        st.write("")

    if sentiment_filter and "Sentiment" in working_df.columns:
        working_df = working_df[working_df["Sentiment"].isin(sentiment_filter)]

    if subclass_filter and "Subclass" in working_df.columns:
        working_df = working_df[working_df["Subclass"].isin(subclass_filter)]

    nlp_meta = st.session_state.get(NLP_META_KEY, {})
    if nlp_meta.get("classifier_accuracy") is not None:
        st.caption(
            f"NLP objection classifier accuracy on held-out data: "
            f"{nlp_meta['classifier_accuracy']:.0%}"
        )

    nlp_columns = [
        "Sentiment",
        "Sentiment_Score",
        "Subclass",
        "NLP_Predicted_Objection",
        "NLP_Prediction_Match",
    ]
    hidden_columns = {"NLP_Topic", "NLP_Topic_Label"}
    leading_columns = [column for column in nlp_columns if column in working_df.columns]
    remaining_columns = [
        column for column in working_df.columns
        if column not in leading_columns and column not in hidden_columns
    ]

    st.dataframe(
        working_df[leading_columns + remaining_columns],
        width="stretch",
    )
