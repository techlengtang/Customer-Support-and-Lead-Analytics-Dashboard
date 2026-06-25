import streamlit as st
import pandas as pd
import plotly.express as px

from utils.nlp import build_word_frequencies, preprocess_text
from utils.nlp_enrichment import NLP_META_KEY
import streamlit as st


SENTIMENT_COLORS = {
    "Positive": "#A8E6CF",
    "Neutral": "#FCE38A",
    "Negative": "#F8B4B4"
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

    icons = {
        "Total Comments": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>',
        "Positive": '<svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>',
        "Neutral": '<svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5"><line x1="5" y1="12" x2="19" y2="12"></line></svg>',
        "Negative": '<svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5"><polyline points="4 18 15 7 20 12"></polyline></svg>'
    }

    
    # icon_colors = {
    #     "Total Comments": "#F97316",
    #     "Positive": "#A9D6BD",
    #     "Neutral": "#FBE9C9",
    #     "Negative": "#F7CAC6"
    # }
    
    # icon_bg_light = {
    #     "Total Comments": "#FFF7ED",
    #     "Positive": "#E0F9F5",
    #     "Neutral": "#FFFBEB",
    #     "Negative": "#FEE9E5"
    # }
    icon_colors = {
        "Total Comments": "#F97316",

        "Positive": "#B8F2E6",
        "Neutral": "#FDEBB9",
        "Negative": "#FDD7D1"
    }

    icon_bg_light = {
        "Total Comments": "#FFF7ED",
        "Positive": "#F4FFFC",
        "Neutral": "#FFFDF8",
        "Negative": "#FFF8F7"
    }
    
    feedback_icons = {
        "Positive": "↑",
        "Neutral": "−",
        "Negative": "↓"
    }

    c1, c2, c3, c4 = st.columns(4)

    metrics_data = [
        ("Total Comments", f"{total:,}", f"{total:,} Reviews"),
        ("Positive", f"{positive_pct:.1f}%", f"{positive} Reviews"),
        ("Neutral", f"{neutral_pct:.1f}%", f"{neutral} Reviews"),
        ("Negative", f"{negative_pct:.1f}%", f"{negative} Reviews")
    ]

    for col, (title, value, count) in zip([c1, c2, c3, c4], metrics_data):
        with col:
            if title == "Total Comments":
                card_html = f'<div class="metric-card"><div class="metric-header"><div class="metric-title">{title}</div><div class="metric-icon" style="background:#FFF7ED;"><svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="#F97316" stroke-width="2" style="stroke-linecap:round; stroke-linejoin:round;"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg></div></div><div style="display:flex; justify-content:space-between; align-items:flex-end;"><div class="metric-value">{value}</div><div style="text-align:right; color:#64748B; font-size:11px; line-height:1.3; padding-bottom:4px;"><div>{count}</div><div>Customer Feedback</div></div></div></div>'
            else:
                accent_color = icon_colors[title]
                feedback_arrow = feedback_icons[title]
                if title == "Positive":
                    svg_icon = '<circle cx="12" cy="12" r="9"></circle><circle cx="9" cy="10" r="1.5" fill="white"></circle><circle cx="15" cy="10" r="1.5" fill="white"></circle><path d="M8 14c1 1.5 2.5 2.5 4 2.5s3-1.5 4-2.5"></path>'
                elif title == "Neutral":
                    svg_icon = '<circle cx="12" cy="12" r="9"></circle><circle cx="9" cy="10" r="1.5" fill="white"></circle><circle cx="15" cy="10" r="1.5" fill="white"></circle><line x1="8" y1="15" x2="16" y2="15" stroke-width="1.5"></line>'
                else:  # Negative
                    svg_icon = '<circle cx="12" cy="12" r="9"></circle><circle cx="9" cy="10" r="1.5" fill="white"></circle><circle cx="15" cy="10" r="1.5" fill="white"></circle><path d="M8 16c1-1.5 2.5-2.5 4-2.5s3 1.5 4 2.5"></path>'
                card_html = f'<div class="metric-card" style="background:white;"><div class="metric-header"><div class="metric-title">{title}</div><div class="metric-icon" style="background:{accent_color}; color:white;"><svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="white" stroke-width="2" style="stroke-linecap:round; stroke-linejoin:round;">{svg_icon}</svg></div></div><div style="display:flex; justify-content:space-between; align-items:flex-end;"><div class="metric-value">{value}</div><div style="text-align:right; color:#64748B; font-size:11px; line-height:1.3; padding-bottom:4px;"><div>{count}</div><div>{feedback_arrow} Feedback</div></div></div></div>'
            st.markdown(card_html, unsafe_allow_html=True)

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
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.20,
                xanchor="center",
                x=0.5,
                title=""
            ),
            legend_title_text=""
        )

        fig.update_traces(
            textinfo="percent",
            textposition="outside",
            textfont=dict(color="#1F2937", size=13),
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
            barmode="stack",
            color_discrete_map=SENTIMENT_COLORS,
        )

        fig.update_layout(
            height=400,
            template="plotly_white",

            paper_bgcolor="white",
            plot_bgcolor="white",

            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.20,
                xanchor="center",
                x=0.2,   # move slightly right
                title=""
            ),

            legend_title_text="",
            margin=dict(
                t=20,
                b=80,
                l=20,
                r=20
            )
        )

        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

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

    fig.update_traces(
        opacity=0.60,
        line=dict(
            width=2.5
        )
    )

    fig.update_layout(
        height=450,
        template="plotly_white",

        paper_bgcolor="white",
        plot_bgcolor="white",

        xaxis_title="Month",
        yaxis_title="Comments",

        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.20,
            xanchor="center",
            x=0.5,
            title=""
        ),

        margin=dict(
            t=20,
            b=80,
            l=20,
            r=20
        )
    )

    st.plotly_chart(
        fig,
        width="stretch",
        config={"displayModeBar": False}
    )

    

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

        row_template = (
            '<tr>'
            '<td style="text-align:left; padding:10px 16px;">{keyword}</td>'
            '<td style="text-align:center; padding:10px 16px;">{count:,}</td>'
            '</tr>'
        )
        rows_html = ''.join(
            row_template.format(keyword=keyword, count=count)
            for keyword, count in negative_keywords
        )

        table_html = (
            '<table style="width:100%; border-collapse:collapse; font-family:Inter, sans-serif; font-size:14px;">'
            '<thead><tr style="background:#F8FAFC; color:#64748B;">'
            '<th style="text-align:left; padding:10px 16px; font-weight:500;">Keyword</th>'
            '<th style="text-align:center; padding:10px 16px; font-weight:500;">Count</th>'
            '</tr></thead>'
            f'<tbody>{rows_html}</tbody>'
            '</table>'
        )

        st.markdown(table_html, unsafe_allow_html=True)

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

    def sentiment_style(val):
        if val == "Positive":
            return "background-color: #E0F9F5; color: #059669"
        elif val == "Neutral":
            return "background-color: #FFFBEB; color: #D97706"
        elif val == "Negative":
            return "background-color: #FEE9E5; color: #DC2626"
        return ""

    display_df = df_sentiment[display_columns]

    if "Sentiment" in display_df.columns:

        styled_df = display_df.style.map(
            sentiment_style,
            subset=["Sentiment"]
        )

        st.dataframe(
            styled_df,
            width="stretch"
        )

    else:

        st.dataframe(
            display_df,
            width="stretch"
        )
