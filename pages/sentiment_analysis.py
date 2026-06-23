import streamlit as st
import pandas as pd
import plotly.express as px

from utils.nlp import build_word_frequencies, preprocess_text
from utils.nlp_enrichment import NLP_META_KEY


SENTIMENT_COLORS = {
    "Positive": "#7BCFA1",
    "Neutral": "#F6C56F",
    "Negative": "#F28B82",
}


def show_sentiment_analysis(df):

    nlp_meta = st.session_state.get(NLP_META_KEY, {})
    df_sentiment = df.copy()

    st.markdown("""
    <div class='page-title'>
        Sentiment Analysis
    </div>

    <div class='page-subtitle'>
        NLP-powered sentiment and language patterns from customer quotes
    </div>
    """, unsafe_allow_html=True)

    if "Sentiment" not in df_sentiment.columns:
        st.warning("NLP sentiment columns are not available for this dataset.")
        return

    total = len(df_sentiment)
    positive = len(df_sentiment[df_sentiment["Sentiment"] == "Positive"])
    neutral = len(df_sentiment[df_sentiment["Sentiment"] == "Neutral"])
    negative = len(df_sentiment[df_sentiment["Sentiment"] == "Negative"])

    positive_pct = positive / total * 100 if total else 0
    neutral_pct = neutral / total * 100 if total else 0
    negative_pct = negative / total * 100 if total else 0

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Comments</div>
            <div class="metric-value">{total:,}</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Positive</div>
            <div class="metric-value">{positive_pct:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Neutral</div>
            <div class="metric-value">{neutral_pct:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Negative</div>
            <div class="metric-value">{negative_pct:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    left, right = st.columns(2)

    with left:
        st.markdown("""
        <div class='chart-title'>
            Sentiment Distribution
        </div>
        """, unsafe_allow_html=True)

        sentiment = (
            df_sentiment["Sentiment"]
            .value_counts()
            .reset_index()
        )
        sentiment.columns = ["Sentiment", "Count"]

        fig = px.pie(
            sentiment,
            names="Sentiment",
            values="Count",
            hole=0.60,
            color="Sentiment",
            color_discrete_map=SENTIMENT_COLORS,
        )

        fig.update_layout(
            height=400,
            template="plotly_white",
            paper_bgcolor="white",
            plot_bgcolor="white",
            legend_orientation="h",
            legend_y=-0.15,
        )

        fig.update_traces(
            textinfo="percent",
            textposition="outside",
            textfont=dict(color="#1F2937", size=15),
        )

        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    with right:
        st.markdown("""
        <div class='chart-title'>
            Top Objection Types by Sentiment
        </div>
        """, unsafe_allow_html=True)

        topics = pd.crosstab(
            df_sentiment["Objection Type"],
            df_sentiment["Sentiment"],
        )
        topics["Total"] = topics.sum(axis=1)
        topics = topics.sort_values("Total", ascending=False).head(8).reset_index()

        fig = px.bar(
            topics,
            y="Objection Type",
            x=["Negative", "Neutral", "Positive"],
            orientation="h",
            barmode="stack",
            color_discrete_map=SENTIMENT_COLORS,
        )

        fig.update_layout(
            height=400,
            template="plotly_white",
            paper_bgcolor="white",
            plot_bgcolor="white",
            legend=dict(orientation="h", y=1.10, x=0.5, xanchor="center"),
            xaxis_title="Number of Comments",
            yaxis_title="",
            margin=dict(l=10, r=10, t=20, b=20),
        )

        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div class='chart-title'>
        Sentiment Trend Over Time
    </div>
    """, unsafe_allow_html=True)

    trend = (
        df_sentiment.groupby(
            [
                pd.Grouper(key="First Contact Date", freq="ME"),
                "Sentiment",
            ]
        )
        .size()
        .reset_index(name="Count")
    )

    trend = trend[trend["First Contact Date"] >= "2025-01-01"]

    fig = px.area(
        trend,
        x="First Contact Date",
        y="Count",
        color="Sentiment",
        color_discrete_map=SENTIMENT_COLORS,
    )

    fig.update_layout(
        height=450,
        template="plotly_white",
        paper_bgcolor="white",
        plot_bgcolor="white",
        legend_orientation="h",
        legend_y=-0.2,
        xaxis_title="Month",
        yaxis_title="Comments",
    )

    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div class='chart-title'>
        Negative Language Signals
    </div>
    """, unsafe_allow_html=True)

    negative_text = df_sentiment.loc[
        df_sentiment["Sentiment"] == "Negative",
        "Quote_English",
    ].dropna().astype(str).map(preprocess_text)
    negative_text = negative_text[negative_text.str.strip() != ""]

    if not negative_text.empty:
        negative_keywords = build_word_frequencies(negative_text, top_n=12)
        st.dataframe(
            pd.DataFrame(negative_keywords, columns=["Keyword", "Count"]),
            use_container_width=True,
            hide_index=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div class='chart-title'>
        NLP-Enriched Customer Comments
    </div>
    """, unsafe_allow_html=True)

    display_columns = [
        "Quote_English",
        "Sentiment",
        "Sentiment_Score",
        "Objection Type",
        "Subclass",
    ]
    display_columns = [column for column in display_columns if column in df_sentiment.columns]

    st.dataframe(
        df_sentiment[display_columns],
        width="stretch",
    )
