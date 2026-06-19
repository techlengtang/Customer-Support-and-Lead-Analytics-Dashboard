import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np


def show_sentiment_analysis(df):

    # =====================================
    # TEMP MOCK DATA
    # =====================================

    np.random.seed(42)

    df_sentiment = df.copy()

    df_sentiment["Sentiment"] = np.random.choice(
        ["Positive", "Neutral", "Negative"],
        size=len(df_sentiment),
        p=[0.25, 0.50, 0.25]
    )

    # =====================================
    # PAGE HEADER
    # =====================================

    st.markdown("""
    <div class='page-title'>
        Sentiment Analysis
    </div>

    <div class='page-subtitle'>
        NLP-powered customer sentiment monitoring
    </div>
    """, unsafe_allow_html=True)

    # =====================================
    # KPI CARDS
    # =====================================

    total = len(df_sentiment)

    positive = len(
        df_sentiment[
            df_sentiment["Sentiment"] == "Positive"
        ]
    )

    neutral = len(
        df_sentiment[
            df_sentiment["Sentiment"] == "Neutral"
        ]
    )

    negative = len(
        df_sentiment[
            df_sentiment["Sentiment"] == "Negative"
        ]
    )

    positive_pct = positive / total * 100
    neutral_pct = neutral / total * 100
    negative_pct = negative / total * 100

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

    # =====================================
    # DONUT + TOP TOPICS
    # =====================================

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

        sentiment.columns = [
            "Sentiment",
            "Count"
        ]

        fig = px.pie(
            sentiment,
            names="Sentiment",
            values="Count",
            hole=0.60,
            color="Sentiment",
            color_discrete_map={
                "Positive": "#7BCFA1",
                "Neutral": "#F6C56F",
                "Negative": "#F28B82"
            }
        )

        fig.update_layout(
            height=400,
            template="plotly_white",
            paper_bgcolor="white",
            plot_bgcolor="white",
            legend_orientation="h",
            legend_y=-0.15
        )

        fig.update_traces(
            textinfo="percent",
            textposition="outside",
            textfont=dict(
                color="#1F2937",
                size=15
            )
        )

        st.plotly_chart(
            fig,
            width="stretch",
            config={"displayModeBar": False}
        )

    with right:

        st.markdown("""
        <div class='chart-title'>
            Top Complaint Topics by Sentiment
        </div>
        """, unsafe_allow_html=True)

        topics = pd.crosstab(
            df_sentiment["Objection Type"],
            df_sentiment["Sentiment"]
        )

        topics["Total"] = topics.sum(axis=1)

        topics = (
            topics
            .sort_values("Total", ascending=False)
            .head(8)
            .reset_index()
        )

        fig = px.bar(
            topics,
            y="Objection Type",
            x=["Negative", "Neutral", "Positive"],
            orientation="h",
            barmode="stack",
            color_discrete_map={
                "Positive": "#7BCFA1",
                "Neutral": "#F6C56F",
                "Negative": "#F28B82"
            }
        )

        fig.update_layout(
            height=420,
            template="plotly_white",
            paper_bgcolor="white",
            plot_bgcolor="white",

            legend=dict(
                orientation="h",
                y=1.10,
                x=0.5,
                xanchor="center"
            ),

            xaxis_title="Number of Comments",
            yaxis_title="",
            margin=dict(
                l=10,
                r=10,
                t=20,
                b=20
            )
        )

        st.plotly_chart(
            fig,
            width="stretch",
            config={"displayModeBar": False}
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # =====================================
    # SENTIMENT TREND
    # =====================================

    st.markdown("""
    <div class='chart-title'>
        Sentiment Trend Over Time
    </div>
    """, unsafe_allow_html=True)

    trend = (
        df_sentiment.groupby(
            [
                pd.Grouper(
                    key="First Contact Date",
                    freq="M"
                ),
                "Sentiment"
            ]
        )
        .size()
        .reset_index(name="Count")
    )

    # Show only from Jan 2025 onwards
    trend = trend[
        trend["First Contact Date"] >= "2025-01-01"
    ]

    fig = px.area(
        trend,
        x="First Contact Date",
        y="Count",
        color="Sentiment",
        color_discrete_map={
            "Positive": "#7BCFA1",
            "Neutral": "#F6C56F",
            "Negative": "#F28B82"
        }
    )
    
    fig.update_layout(
        height=450,
        template="plotly_white",
        paper_bgcolor="white",
        plot_bgcolor="white",
        legend_orientation="h",
        legend_y=-0.2,
        xaxis_title="Month",
        yaxis_title="Comments"
    )

    
    st.plotly_chart(
        fig,
        width="stretch",
        config={"displayModeBar": False}
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # =====================================
    # CUSTOMER COMMENTS
    # =====================================

    st.markdown("""
    <div class='chart-title'>
        Customer Comments
    </div>
    """, unsafe_allow_html=True)

    st.dataframe(
        df_sentiment[
            [
                "Quote_English",
                "Sentiment",
                "Objection Type"
            ]
        ],
        width="stretch"
    )