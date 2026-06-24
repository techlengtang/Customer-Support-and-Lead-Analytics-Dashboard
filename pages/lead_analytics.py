import streamlit as st
import pandas as pd
import plotly.express as px


def show_lead_analytics(df):

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    st.markdown("""
    <div class='page-title'>Lead Analytics</div>
    <div class='page-subtitle'>
        Analyze lead quality, conversion performance, and NLP language signals
    </div>
    """, unsafe_allow_html=True)

    # =========================
    # KPI CARDS
    # =========================
    c1, c2, c3, c4 = st.columns(4)
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
    details = {
        "Total Leads": (
            f"{total_leads:,} Records",
            "Lead Pipeline"
        ),

        "Qualified Leads": (
            f"{qualified:,} Leads",
            "Ready to Convert"
        ),

        "Converted Leads": (
            f"{converted:,} Customers",
            "Successful Conversions"
        ),

        "Conversion Rate": (
            f"{conversion_rate:.1f}%",
            "Lead Efficiency"
        )
    }

    icons = {
        "Total Leads": '<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>',
        "Qualified Leads": '<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"></path></svg>',
        "Converted Leads": '<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>',
        "Conversion Rate": '<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>'
    }

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
            display_value = (
                f"{value:,}"
                if isinstance(value, (int, float))
                else str(value)
            )
            detail_1, detail_2 = details[title]
            card_html = f'<div class="metric-card" style="background:white;"><div class="metric-header"><div class="metric-title">{title}</div><div class="metric-icon">{icons[title]}</div></div><div style="display:flex; justify-content:space-between; align-items:flex-end;"><div class="metric-value">{display_value}</div><div style="text-align:right; color:#64748B; font-size:11px; line-height:1.3; padding-bottom:4px;"><div>{detail_1}</div><div>{detail_2}</div></div></div></div>'
            st.markdown(card_html, unsafe_allow_html=True)

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

        lead_order = [
            "Converted",
            "Qualified",
            "Unqualified",
            "Lost"
        ]

        for col in lead_order:
            if col not in platform.columns:
                platform[col] = 0

        platform = platform[["Platform"] + lead_order]

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
            color_discrete_map={
                "Converted": "#FF6B00",      # Dark Orange
                "Qualified": "#F58A32",      # Orange
                "Unqualified": "#F0B66D",    # Medium Light
                "Lost": "#F5D7A8"            # Lightest
            }
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
                "HK": "Hong Kong",
                "TH": "Thailand",
                "USA": "United States",
                "MY": "Malaysia",
                "VN": "Vietnam",
                "AE": "United Arab Emirates",
                "NZ": "New Zealand",
                "TR": "Turkey",
            })
            .fillna("Other")
        )

        destination = pd.crosstab(
            destination_df["Destination"],
            destination_df["Lead Quality"]
        ).reset_index()

        lead_order = [
            "Converted",
            "Qualified",
            "Unqualified",
            "Lost"
        ]

        for col in lead_order:
            if col not in destination.columns:
                destination[col] = 0

        destination = destination[["Destination"] + lead_order]

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
        # Calculate total leads
        destination["Total"] = destination.iloc[:, 1:].sum(axis=1)

        # Keep Top 6 countries only
        destination = (
            destination
            .sort_values("Total", ascending=False)
            .head(6)
        )

        # Remove helper column
        destination = destination.drop(columns="Total")

        fig = px.bar(
            destination,
            x="Destination",
            y=destination.columns[1:],
            barmode="stack",
            color_discrete_map={
                "Converted": "#FF6B00",      # Dark Orange
                "Qualified": "#F58A32",      # Orange
                "Unqualified": "#F0B66D",    # Medium Light
                "Lost": "#F5D7A8"            # Lightest
            }
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

    if "Sentiment" in df.columns and "Lead Quality" in df.columns:
        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("""
        <div class='chart-title'>
            NLP Sentiment by Lead Quality
        </div>
        """, unsafe_allow_html=True)

        sentiment_lead = pd.crosstab(
            df["Lead Quality"],
            df["Sentiment"],
        ).reset_index()

        fig = px.bar(
            sentiment_lead,
            x="Lead Quality",
            y=["Negative", "Neutral", "Positive"],
            barmode="stack",
            color_discrete_map={
                "Positive": "#A8E6CF",
                "Neutral": "#FCE38A",
                "Negative": "#F8B4B4"
            },
        )
        fig.update_layout(
            height=420,
            template="plotly_white",
            paper_bgcolor="white",
            plot_bgcolor="white",
            xaxis_title="",
            yaxis_title="Quotes",
            legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"),
        )
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    if "Subclass" in df.columns:
        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("""
        <div class='chart-title'>
            Top NLP Subclasses in Converted vs Lost Leads
        </div>
        """, unsafe_allow_html=True)

        subclass_compare = df[df["Lead Quality"].isin(["Converted", "Lost"])].copy()
        if not subclass_compare.empty:
            subclass_counts = (
                subclass_compare.groupby(["Lead Quality", "Subclass"])
                .size()
                .reset_index(name="Count")
            )
            top_subclasses = (
                subclass_counts.groupby("Subclass")["Count"]
                .sum()
                .nlargest(8)
                .index
            )
            subclass_counts = subclass_counts[
                subclass_counts["Subclass"].isin(top_subclasses)
            ]

            fig = px.bar(
                subclass_counts,
                x="Subclass",
                y="Count",
                color="Lead Quality",
                barmode="group",
                color_discrete_map={
                "Converted": "#FF6B00",      # Dark Orange
                "Lost": "#F5D7A8" 
                },
            )
            fig.update_layout(
                height=420,
                template="plotly_white",
                paper_bgcolor="white",
                plot_bgcolor="white",
                xaxis_title="",
                yaxis_title="Quotes",
                legend=dict(orientation="h", y=-0.25, x=0.5, xanchor="center"),
            )
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})