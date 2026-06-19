import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff



def show_objection_analysis(df):

    st.markdown("""
    <div class='page-title'>Objection Analysis</div>
    <div class='page-subtitle'>
        Deep dive into customer objections and concerns
    </div>
    """, unsafe_allow_html=True)

    # =========================
    # KPI CARDS
    # =========================

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

            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title">{title}</div>
                    <div class="metric-value">{value:,}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("<br>", unsafe_allow_html=True)

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
    # =========================
    # CUSTOMER QUOTES
    # =========================

    st.markdown("""
    <div class='chart-title'>
        Customer Objections
    </div>
    """, unsafe_allow_html=True)

    st.dataframe(
        df[
            [
                "Objection Type",
                "Quote_English",
                "Lead Quality"
            ]
        ],
        width="stretch"
    )