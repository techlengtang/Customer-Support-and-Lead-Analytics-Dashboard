import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff

from utils.paths import get_config_path
from utils.subclass_charts import (
    get_subclass_summaries_from_df,
    render_all_subclass_charts,
    render_cluster_catalog,
    render_objection_class_overview,
)
from utils.wordcloud_viz import render_objection_wordcloud_section



def show_objection_analysis(df):

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    st.markdown("""
    <div class='page-title'>Objection Analysis</div>
    <div class='page-subtitle'>
        Deep dive into customer objections, NLP language patterns, and subclasses
    </div>
    """, unsafe_allow_html=True)

    # =========================
    # KPI CARDS
    # =========================

    icons = {
        "Total Objections": '<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"></rect><line x1="8" y1="8" x2="16" y2="8"></line><line x1="8" y1="12" x2="16" y2="12"></line><line x1="8" y1="16" x2="12" y2="16"></line></svg>',
        "Categories": '<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L15.09 8.26H22L17.45 12.88L19.54 19.12L12 15.77L4.46 19.12L6.55 12.88L2 8.26H8.91L12 2Z"></path></svg>',
        "Open Cases": '<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>',
        "Platforms": '<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>'
    }

    c1, c2, c3, c4 = st.columns(4)

    metrics = [
        ("Total Objections", len(df)),
        ("Categories", df["Objection Type"].nunique()),
        ("Open Cases", len(df[df["Objection Status"] == "Unsolved"])),
        ("Platforms", df["Main Contact Platform"].nunique())
    ]

    for col, (title, value) in zip(
        [c1, c2, c3, c4],
        metrics
    ):

        with col:
            svg_content = icons[title].replace('<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2">', '').replace('</svg>', '')
            card_html = f'<div class="metric-card"><div class="metric-header"><div class="metric-title">{title}</div><div class="metric-icon" style="background-color: #FFF7ED;"><svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="#F97316" stroke-width="2" style="stroke-linecap: round; stroke-linejoin: round;">{svg_content}</svg></div></div><div class="metric-value">{value:,}</div></div>'
            st.markdown(card_html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # =========================
    # WORD CLOUD
    # =========================

    render_objection_wordcloud_section(df)

    # =========================
    # MONTHLY TREND
    # =========================

    left, right = st.columns(2)

    with left:

        st.markdown("""
        <div class='chart-title'>
            Monthly Objection Trend
        </div>
        """, unsafe_allow_html=True)

        trend = (
            df.groupby(
                df["First Contact Date"].dt.to_period("M")
            )
            .size()
            .reset_index(name="Count")
        )

        trend["First Contact Date"] = (
            trend["First Contact Date"]
            .astype(str)
        )

        fig = px.area(
            trend,
            x="First Contact Date",
            y="Count",
            color_discrete_sequence=["#F97316"]
        )

        fig.update_layout(
            height=350,
            template="plotly_white",
            paper_bgcolor="white",
            plot_bgcolor="white"
        )
        
        st.plotly_chart(
            fig,
            width="stretch",
            config={"displayModeBar": False}
        )

    with right:

        st.markdown("""
        <div class='chart-title'>
            Objection by Platform
        </div>
        """, unsafe_allow_html=True)

        platform = (
            df["Main Contact Platform"]
            .value_counts()
            .reset_index()
        )

        platform.columns = [
            "Platform",
            "Count"
        ]

        fig = px.pie(
            platform,
            names="Platform",
            values="Count",
            hole=0.6,
            color_discrete_sequence=px.colors.sequential.Oranges_r
        )

        fig.update_layout(
            height=350
        )

        st.plotly_chart(
            fig,
            width="stretch",
            config={"displayModeBar": False}
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # =========================
    # OBJECTION TYPE BY DESTINATION
    # =========================

    st.markdown("""
    <div class='chart-title'>
        Objection Type by Destination Country
    </div>
    """, unsafe_allow_html=True)

    df_heatmap = df.copy()

    df_heatmap["Destination"] = (
        df_heatmap["Service"]
        .str.extract(
            r"VISA[- ]([A-Z]{2})",
            expand=False
        )
    )

    df_heatmap["Destination"] = (
        df_heatmap["Destination"]
        .fillna("OTHER")
    )

    heatmap = pd.crosstab(
        df_heatmap["Objection Type"],
        df_heatmap["Destination"]
    )

    fig = ff.create_annotated_heatmap(
        z=heatmap.values,
        x=heatmap.columns.tolist(),
        y=heatmap.index.tolist(),
        annotation_text=heatmap.values.astype(str),
        colorscale="Oranges",
        showscale=True
    )

    fig.update_layout(
        height=550,
        template="plotly_white",
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(
            l=20,
            r=20,
            t=40,
            b=20
        ),
        xaxis_title="Destination Country",
        yaxis_title="Objection Type"
    )

    st.plotly_chart(
        fig,
        width="stretch",
        config={"displayModeBar": False}
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # =========================
    # OBJECTION CLASS OVERVIEW
    # =========================

    render_objection_class_overview(df)

    # =========================
    # CLUSTER CATALOG
    # =========================

    render_cluster_catalog()

    # =========================
    # SUBCLASS BREAKDOWN
    # =========================

    subclass_result = get_subclass_summaries_from_df(df)
    if subclass_result is None:
        rules_path = get_config_path('subclass_rules.json')
        if not rules_path.exists():
            st.info(
                f'Subclass breakdown is unavailable. Missing rules file at `{rules_path}`.'
            )
        else:
            st.info('Subclass breakdown is unavailable for the current dataset.')
    else:
        render_all_subclass_charts(subclass_result['summary'], columns=2)

    st.markdown("<br>", unsafe_allow_html=True)

    # =========================
    # CUSTOMER QUOTES
    # =========================

    st.markdown("""
    <div class='chart-title'>
        Customer Objections
    </div>
    """, unsafe_allow_html=True)

    quote_columns = [
        "Objection Type",
        "Subclass",
        "Sentiment",
        "Quote_English",
        "Lead Quality",
    ]
    quote_columns = [column for column in quote_columns if column in df.columns]

    st.dataframe(
        df[quote_columns],
        width="stretch"
    )