import streamlit as st
import pandas as pd

from utils.nlp import (
    apply_subclass_rules,
    assign_topics_to_texts,
    predict_sentiment,
    preprocess_text,
    train_objection_classifier,
)
from utils.subclass_charts import _load_subclass_rules

NLP_META_KEY = 'nlp_meta'
TEXT_COLUMN = 'Quote_English'
LABEL_COLUMN = 'Objection Type'


def _build_subclass_summary(df, assignments):
    summary = {}
    if assignments is None or assignments.empty:
        return summary

    grouped = assignments.groupby(['class', 'subclass']).size().reset_index(name='count')
    for class_name in grouped['class'].unique():
        class_rows = grouped[grouped['class'] == class_name][['subclass', 'count']]
        summary[class_name] = class_rows.sort_values('count', ascending=False).to_dict('records')

    return summary


def _enrich_dataframe(df):
    enriched = df.copy()
    meta = {
        'classifier_accuracy': None,
        'topic_terms': [],
        'topic_distribution': [],
    }

    if TEXT_COLUMN not in enriched.columns:
        return enriched, meta

    quotes = enriched[TEXT_COLUMN].fillna('').astype(str)
    enriched['Clean_Text'] = quotes.map(preprocess_text)

    sentiments = []
    scores = []
    for quote in quotes:
        label, score = predict_sentiment(quote)
        sentiments.append(label)
        scores.append(score)

    enriched['Sentiment'] = sentiments
    enriched['Sentiment_Score'] = scores
    enriched['Subclass'] = 'Unspecified'

    valid_index = enriched.index[enriched['Clean_Text'].str.strip() != '']
    if len(valid_index) > 0 and LABEL_COLUMN in enriched.columns:
        rules = _load_subclass_rules()
        if rules is not None:
            texts = enriched.loc[valid_index, 'Clean_Text'].tolist()
            labels = enriched.loc[valid_index, LABEL_COLUMN].astype(str).tolist()
            subclass_result = apply_subclass_rules(texts, labels, rules)
            if subclass_result and not subclass_result['assignments'].empty:
                enriched.loc[valid_index, 'Subclass'] = (
                    subclass_result['assignments']['subclass'].values
                )
                meta['subclass_summary'] = _build_subclass_summary(
                    enriched,
                    subclass_result['assignments'],
                )

    topic_names, topic_labels, topic_terms, topic_distribution = assign_topics_to_texts(
        quotes.tolist()
    )
    enriched['NLP_Topic'] = topic_names
    enriched['NLP_Topic_Label'] = topic_labels
    meta['topic_terms'] = topic_terms
    meta['topic_distribution'] = topic_distribution

    if LABEL_COLUMN in enriched.columns and len(enriched) >= 30:
        model_result = train_objection_classifier(
            enriched['Clean_Text'],
            enriched[LABEL_COLUMN],
        )
        if model_result is not None:
            enriched['NLP_Predicted_Objection'] = model_result['model'].predict(
                enriched['Clean_Text']
            )
            enriched['NLP_Prediction_Match'] = (
                enriched['NLP_Predicted_Objection'] == enriched[LABEL_COLUMN]
            )
            meta['classifier_accuracy'] = model_result['accuracy']
            meta['top_features'] = model_result['top_features']

    return enriched, meta


@st.cache_data(show_spinner='Running NLP analysis on customer quotes...')
def get_enriched_dataframe(df: pd.DataFrame):
    enriched, meta = _enrich_dataframe(df)
    return enriched, meta


def ensure_nlp_enriched(df):
    if 'Sentiment' in df.columns and 'Subclass' in df.columns:
        return df, st.session_state.get(NLP_META_KEY, {})

    enriched, meta = get_enriched_dataframe(df)
    st.session_state[NLP_META_KEY] = meta
    return enriched, meta
