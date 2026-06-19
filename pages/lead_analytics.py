import streamlit as st
import pandas as pd
import plotly.express as px


def show_lead_analytics(df):

    st.markdown("""
    <div class='page-title'>Lead Analytics</div>
    <div class='page-subtitle'>
        Analyze lead quality, conversion performance, and acquisition effectiveness
    </div>
    """, unsafe_allow_html=True)

    # =========================
    # KPI CARDS
    # =========================

    total_leads = len(df)

    qualified = len(
        df[df["Lead Quality"] == "Qualified"]
    )

    converted = len(
        df[df["Lead Quality"] == "Converted"]
    )

    conversion_rate = (
        round(
            converted / total_leads * 100,
            1
        )
        if total_leads > 0
        else 0
    )

    c1, c2, c3, c4 = st.columns(4)

    metrics = [
        ("Total Leads", total_leads),
        ("Qualified Leads", qualified),
        ("Converted Leads", converted),
        ("Conversion Rate", f"{conversion_rate}%")
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
                    <div class="metric-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # =========================
    # MONTHLY LEAD TREND
    # =========================

    st.markdown("""
    <div class='chart-title'>
        Monthly Lead Quality Trend
    </div>
    """, unsafe_allow_html=True)

    trend = (
        df.groupby(
            [
                df["First Contact Date"].dt.to_period("M"),
                "Lead Quality"
            ]
        )
        .size()
        .reset_index(name="Count")
    )

    trend["First Contact Date"] = (
        trend["First Contact Date"]
        .astype(str)
    )

    fig = px.line(
        trend,
        x="First Contact Date",
        y="Count",
        color="Lead Quality",
        markers=True,
        color_discrete_sequence=px.colors.qualitative.Set2
    )

    fig.update_layout(
        height=500,
        template="plotly_white",
        paper_bgcolor="white",
        plot_bgcolor="white",
        hovermode="x unified",

        xaxis_title="Month",
        yaxis_title="Leads",

        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.30,
            xanchor="center",
            x=0.5,
            title_text=""
        ),

        margin=dict(
            t=30,
            b=100,
            l=20,
            r=20
        )
    )

    fig.update_xaxes(
        tickmode="linear",
        dtick="M4",
        tickformat="%b %Y",
        tickangle=-45
    )

    st.plotly_chart(
        fig,
        width="stretch",
        config={"displayModeBar": False}
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # =========================
    # PLATFORM + DESTINATION
    # =========================

    left, right = st.columns(2)

    with left:

        st.markdown("""
        <div class='chart-title'>
            Lead Quality by Platform
        </div>
        """, unsafe_allow_html=True)

        platform_df = df.copy()

        platform_df["Platform"] = (
            platform_df["Main Contact Platform"]
            .replace({
                "Facebook - Explorer Travel Agency": "Facebook Page",
                "Facebook - Explorer by SL": "Facebook SL",
                "Telegram - DM": "Telegram",
                "Webapp": "Website"
            })
        )

        platform = pd.crosstab(
            platform_df["Platform"],
            platform_df["Lead Quality"]
        ).reset_index()

        # Sort by total leads
        platform["Total"] = (
            platform.iloc[:, 1:]
            .sum(axis=1)
        )

        platform = (
            platform
            .sort_values(
                "Total",
                ascending=False
            )
            .drop(columns="Total")
        )

        fig = px.bar(
            platform,
            x="Platform",
            y=platform.columns[1:],
            barmode="group",
            color_discrete_sequence=[
                "#F5D7A8",
                "#F0B66D",
                "#F58A32",
                "#FF6B00",
                "#D9480F"
            ]
        )

        fig.update_layout(

            height=450,

            template="plotly_white",

            paper_bgcolor="white",
            plot_bgcolor="white",

            xaxis_title="",
            yaxis_title="Leads",

            font=dict(
                family="Inter",
                size=13,
                color="#1F2937"
            ),

            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.22,
                xanchor="center",
                x=0.5,
                title=""
            ),

            margin=dict(
                t=40,
                b=100,
                l=20,
                r=20
            )
        )

        fig.update_xaxes(
            tickangle=0,
            tickfont=dict(
                size=12,
                color="#6B7280"
            )
        )

        fig.update_yaxes(
            tickfont=dict(
                size=12,
                color="#6B7280"
            )
        )

        st.plotly_chart(
            fig,
            width="stretch",
            config={
                "displayModeBar": False
            }
        )

    with right:

        st.markdown("""
        <div class='chart-title'>
            Lead Distribution by Destination Country
        </div>
        """, unsafe_allow_html=True)

        destination_df = df.copy()

        # Extract country code
        destination_df["Destination"] = (
            destination_df["Service"]
            .str.extract(
                r"VISA[- ]([A-Z]{2})",
                expand=False
            )
        )

        # Convert code to country name
        destination_df["Destination"] = (
            destination_df["Destination"]
            .replace({
                "AU": "Australia",
                "JP": "Japan",
                "KR": "Korea",
                "CN": "China",
                "US": "USA",
                "EU": "Europe",
                "CA": "Canada",
                "HK": "Hong Kong"
            })
            .fillna("Other")
        )

        destination = pd.crosstab(
            destination_df["Destination"],
            destination_df["Lead Quality"]
        ).reset_index()

        # Sort by total leads
        destination["Total"] = (
            destination.iloc[:, 1:]
            .sum(axis=1)
        )

        destination = (
            destination
            .sort_values(
                "Total",
                ascending=False
            )
            .drop(
                columns="Total"
            )
        )

        fig = px.bar(
            destination,
            x="Destination",
            y=destination.columns[1:],
            barmode="stack",
            color_discrete_sequence=[
                "#F5D7A8",
                "#F0B66D",
                "#F58A32",
                "#FF6B00",
                "#D9480F"
            ]
        )

        fig.update_layout(

            height=450,

            template="plotly_white",

            paper_bgcolor="white",
            plot_bgcolor="white",

            xaxis_title="",
            yaxis_title="Leads",

            font=dict(
                family="Inter",
                size=13,
                color="#1F2937"
            ),

            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.25,
                xanchor="center",
                x=0.5,
                title=""
            ),

            margin=dict(
                t=40,
                b=120,
                l=20,
                r=20
            )
        )

        fig.update_xaxes(
            tickfont=dict(
                size=12,
                color="#6B7280"
            )
        )

        fig.update_yaxes(
            tickfont=dict(
                size=12,
                color="#6B7280"
            )
        )

        st.plotly_chart(
            fig,
            width="stretch",
            config={
                "displayModeBar": False
            }
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # =========================
    # CONVERSION RATE
    # =========================

    st.markdown("""
    <div class='chart-title'>
        Conversion Rate by Destination
    </div>
    """, unsafe_allow_html=True)

    conversion_df = destination_df.copy()

    conversion = (
        conversion_df
        .groupby("Destination")
        .apply(
            lambda x:
            (
                (x["Lead Quality"] == "Converted").sum()
                / len(x)
            ) * 100
        )
        .reset_index(name="Conversion Rate")
    )

    conversion = (
        conversion
        .sort_values(
            "Conversion Rate",
            ascending=False
        )
    )

    fig = px.bar(
        conversion,
        x="Conversion Rate",
        y="Destination",
        orientation="h",
        text="Conversion Rate",
        color="Conversion Rate",
        color_continuous_scale="Oranges"
    )

    fig.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside",
        textfont=dict(
            color="#6B7280",
            size=14
        )
    )

    fig.update_layout(
        height=450,
        template="plotly_white",
        paper_bgcolor="white",
        plot_bgcolor="white",
        coloraxis_showscale=False,
        xaxis_title="Conversion Rate (%)",
        yaxis_title=""
    )

    st.plotly_chart(
        fig,
        width="stretch",
        config={"displayModeBar": False}
    )