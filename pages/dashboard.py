import streamlit as st
import plotly.express as px

from utils.load_data import load_uploaded_data
from utils.nlp_enrichment import NLP_META_KEY

ORANGE = [
    "#FED7AA",
    "#FDBA74",
    "#FB923C",
    "#F97316"
]

def show_dashboard(df):

    # ======================
    # HEADER
    # ======================

    st.markdown("""
    <div class='page-title'>
        Customer Support and Lead Analytics Dashboard
    </div>

    <div class='page-subtitle'>
        Customer Support Intelligence Platform powered by NLP
    </div>
    """, unsafe_allow_html=True)

    with st.container(border=True):

        upload_col, status_col = st.columns([2, 1])

        with upload_col:

            uploaded_file = st.file_uploader(
                "Upload dashboard data",
                type=[
                    "csv",
                    "xlsx",
                    "xls"
                ],
                help="Upload a CSV or Excel file with the same dashboard columns."
            )

        if uploaded_file is not None:

            try:

                df = load_uploaded_data(uploaded_file)
                st.session_state["dashboard_df"] = df
                st.session_state["dashboard_data_name"] = uploaded_file.name
                st.success(
                    f"Loaded {uploaded_file.name} with {len(df):,} records."
                )

            except Exception as exc:

                st.error(
                    f"Could not load this file. {exc}"
                )

        with status_col:

            active_file = st.session_state.get(
                "dashboard_data_name",
                "Default dataset"
            )

            st.markdown(
                f"""
                <div class="upload-status">
                    <div class="upload-status-label">Active Data</div>
                    <div class="upload-status-value">{active_file}</div>
                    <div class="upload-status-meta">{len(df):,} records</div>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown(
                "<div class='upload-reset-spacer'></div>",
                unsafe_allow_html=True
            )

            if st.button("Use default data"):

                st.session_state.pop("dashboard_df", None)
                st.session_state.pop("dashboard_data_name", None)
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
# ======================
# FILTERS
# ======================

    f1, f2, f3, f4 = st.columns(4)

    with f1:
        service_filter = st.selectbox(
            "Service",
            ["All"] + sorted(df["Service"].dropna().unique())
        )

    with f2:
        platform_filter = st.selectbox(
            "Platform",
            ["All"] + sorted(df["Main Contact Platform"].dropna().unique())
        )

    with f3:
        lead_filter = st.selectbox(
            "Lead Quality",
            ["All"] + sorted(df["Lead Quality"].dropna().unique())
        )

    with f4:
        objection_filter = st.selectbox(
            "Objection Type",
            ["All"] + sorted(df["Objection Type"].dropna().unique())
        )

    filtered_df = df.copy()

    if service_filter != "All":
        filtered_df = filtered_df[
            filtered_df["Service"] == service_filter
        ]

    if platform_filter != "All":
        filtered_df = filtered_df[
            filtered_df["Main Contact Platform"] == platform_filter
        ]

    if lead_filter != "All":
        filtered_df = filtered_df[
            filtered_df["Lead Quality"] == lead_filter
        ]

    if objection_filter != "All":
        filtered_df = filtered_df[
            filtered_df["Objection Type"] == objection_filter
        ]

    st.markdown("<br>", unsafe_allow_html=True)
    # ======================
    # KPI CARDS
    # ======================

    c1, c2, c3, c4 = st.columns(4)

    open_cases = len(
        filtered_df[
            filtered_df["Objection Status"] == "Unsolved"
        ]
    )

    converted = len(
        filtered_df[
            filtered_df["Lead Quality"] == "Converted"
        ]
    )

    metrics = [
        ("Total Records", len(filtered_df)),
        ("Open Cases", open_cases),
        ("Converted", converted),
        ("Objection Types", filtered_df["Objection Type"].nunique())
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

            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title">{title}</div>
                    <div class="metric-value">{display_value}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.write("")

    st.markdown("<br>", unsafe_allow_html=True)

    if not filtered_df.empty:

        top_objection = (
            filtered_df["Objection Type"]
            .value_counts()
            .idxmax()
        )

        top_platform = (
            filtered_df["Main Contact Platform"]
            .value_counts()
            .idxmax()
        )

        top_lead = (
            filtered_df["Lead Quality"]
            .value_counts()
            .idxmax()
        )

        dominant_sentiment = "-"
        negative_pct = 0
        top_subclass = "-"
        if "Sentiment" in filtered_df.columns:
            dominant_sentiment = (
                filtered_df["Sentiment"]
                .value_counts()
                .idxmax()
            )
            negative_pct = (
                len(filtered_df[filtered_df["Sentiment"] == "Negative"])
                / len(filtered_df)
                * 100
            )
        if "Subclass" in filtered_df.columns:
            top_subclass = (
                filtered_df["Subclass"]
                .value_counts()
                .idxmax()
            )

    else:

        top_objection = "-"
        top_platform = "-"
        top_lead = "-"
        dominant_sentiment = "-"
        negative_pct = 0
        top_subclass = "-"

    nlp_meta = st.session_state.get(NLP_META_KEY, {})
    classifier_accuracy = nlp_meta.get("classifier_accuracy")
    classifier_line = (
        f"• NLP classifier accuracy: <b>{classifier_accuracy:.0%}</b><br>"
        if classifier_accuracy is not None
        else ""
    )

    st.markdown(
        f"""
        <div class='insight-card'>
        <h4>Business Insights</h4>

        • Most common objection:
        <b>{top_objection}</b><br>

        • Highest inquiry source:
        <b>{top_platform}</b><br>

        • Most common lead quality:
        <b>{top_lead}</b><br>

        • Dominant customer sentiment:
        <b>{dominant_sentiment}</b> ({negative_pct:.1f}% negative)<br>

        • Top NLP subclass signal:
        <b>{top_subclass}</b><br>

        {classifier_line}

        • Total records analyzed:
        <b>{len(filtered_df)}</b>

        </div>
        """,
        unsafe_allow_html=True
    )

    if "Sentiment" in filtered_df.columns and not filtered_df.empty:
        st.markdown("""
        <div class="chart-title">
            NLP Sentiment Overview
        </div>
        """, unsafe_allow_html=True)

        nlp_left, nlp_right = st.columns(2)

        with nlp_left:
            sentiment_counts = (
                filtered_df["Sentiment"]
                .value_counts()
                .reset_index()
            )
            sentiment_counts.columns = ["Sentiment", "Count"]

            fig = px.pie(
                sentiment_counts,
                names="Sentiment",
                values="Count",
                hole=0.55,
                color="Sentiment",
                color_discrete_map={
                    "Positive": "#7BCFA1",
                    "Neutral": "#F6C56F",
                    "Negative": "#F28B82",
                },
            )
            fig.update_layout(
                height=320,
                template="plotly_white",
                paper_bgcolor="white",
                plot_bgcolor="white",
                showlegend=True,
            )
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

        with nlp_right:
            if "NLP_Topic" in filtered_df.columns:
                topic_counts = (
                    filtered_df["NLP_Topic"]
                    .value_counts()
                    .reset_index()
                )
                topic_counts.columns = ["Topic", "Count"]
                topic_counts = topic_counts[topic_counts["Topic"] != "Unassigned"]

                fig = px.bar(
                    topic_counts,
                    x="Count",
                    y="Topic",
                    orientation="h",
                    color="Count",
                    color_continuous_scale="Oranges",
                    text="Count",
                )
                fig.update_layout(
                    height=320,
                    template="plotly_white",
                    coloraxis_showscale=False,
                    margin=dict(l=10, r=20, t=10, b=10),
                )
                st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

        st.markdown("<br>", unsafe_allow_html=True)
    # ======================
    # MONTHLY TREND
    # ======================

    st.markdown("""
    <div class="chart-title">
        Customer Inquiry Trend
    </div>
    """, unsafe_allow_html=True)

    monthly = (
        filtered_df.groupby(
            filtered_df["First Contact Date"].dt.to_period("M")
        )
        .size()
        .reset_index(name="Count")
    )

    monthly["First Contact Date"] = (
        monthly["First Contact Date"]
        .astype(str)
    )

    fig = px.line(
        monthly,
        x="First Contact Date",
        y="Count",
        markers=True
    )

    fig.update_traces(
        line=dict(
            color="#FB923C",
            width=4
        )
    )

    fig.update_layout(
        height=300,
        template="plotly_white",
        margin=dict(
            l=20,
            r=20,
            t=10,
            b=10
        ),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(
            family="Inter",
            size=13,
            color="#1F2937"
        ),
        xaxis_title="",
        yaxis_title=""
    )

    st.plotly_chart(
        fig,
        width="stretch",
        config={"displayModeBar": False}
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ======================
    # ROW 2
    # ======================

    left, right = st.columns([2, 1])

    with left:

        st.markdown("""
        <div class="chart-title">
            Top Objection Types
        </div>
        """, unsafe_allow_html=True)

        objection = (
            filtered_df["Objection Type"]
            .value_counts()
            .head(10)
            .reset_index()
        )

        objection.columns = [
            "Objection Type",
            "Count"
        ]

        fig = px.bar(
            objection,
            x="Count",
            y="Objection Type",
            orientation="h",
            color="Count",
            color_continuous_scale="Oranges",
            text="Count"
        )
        fig.update_traces(
            texttemplate="%{x:,}",
            textposition="outside",
            textfont=dict(
                size=12,
                color="#6B7280",
                family="Inter"
            ),
            cliponaxis=False
        )

        fig.update_layout(
            height=350,

            legend=dict(
                orientation="h",
                y=-0.15,
                x=0.5,
                xanchor="center"
            ),

            font=dict(
                family="Inter",
                size=13,
                color="#1F2937"
            ),

            margin=dict(
                l=10,
                r=10,
                t=10,
                b=60
            ),

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
        <div class="chart-title">
            Lead Quality
        </div>
        """, unsafe_allow_html=True)

        lead = (
    filtered_df["Lead Quality"]
    .value_counts()
    .reset_index()
)

        lead.columns = [
            "Lead Quality",
            "Count"
        ]

        # Calculate percentage
        lead["Percentage"] = (
            lead["Count"]
            / lead["Count"].sum()
            * 100
        )

        # Create custom labels
        lead["Label"] = (
            lead["Lead Quality"]
            + " ("
            + lead["Percentage"].round(1).astype(str)
            + "%)"
        )

        fig = px.pie(
            lead,
            names="Label",
            values="Count",
            hole=0.65,
            color_discrete_sequence=[
                "#F5D7A8",
                "#F0B66D",
                "#F58A32",
                "#FF6B00",
                "#E65100"
            ]
        )

        fig.update_traces(
            textinfo="none"
        )

        fig.update_layout(
            height=350,
            margin=dict(l=20, r=20, t=20, b=20),

            legend=dict(
                orientation="h",
                y=-0.15,
                x=0.5,
                xanchor="center"
            )
        )


        st.plotly_chart(
            fig,
            width="stretch",
            config={"displayModeBar": False}
        )
    st.markdown("<br>", unsafe_allow_html=True)

    # ======================
    # ROW 3
    # ======================

    left, right = st.columns(2)

    with left:

        st.markdown("""
        <div class="chart-title">
            Service Distribution
        </div>
        """, unsafe_allow_html=True)

        service = (
            filtered_df["Service"]
            .value_counts()
            .head(10)
            .reset_index()
        )

        service.columns = [
            "Service",
            "Count"
        ]
        service["Short Service"] = (
    service["Service"]
    .str.extract(
        r"(VISA-[A-Z]{2}|VISA\s-\s[A-Z]{2})",
        expand=False
    )
)

        service["Short Service"] = (
            service["Short Service"]
            .str.replace("VISA - ", "VISA-", regex=False)
            .fillna("Other")
        )

        # Combine KHM + FOR into one VISA type
        service = (
            service.groupby("Short Service", as_index=False)
            .agg({"Count": "sum"})
            .sort_values("Count", ascending=False)
        )

        fig = px.bar(
            service,
            x="Short Service",
            y="Count",
            color="Count",
            color_continuous_scale="Oranges"
        )
        fig.update_layout(
            height=320,
            template="plotly_white",
            paper_bgcolor="white",
            plot_bgcolor="white",
            font=dict(
                family="Inter",
                size=13,
                color="#6B7280"
            ),
            xaxis_title="",
            yaxis_title="Count",
            coloraxis_showscale=False
        )

        st.plotly_chart(
            fig,
            width="stretch",
            config={"displayModeBar": False}
        )

    with right:

        st.markdown("""
        <div class="chart-title">
            Marketing Sources
        </div>
        """, unsafe_allow_html=True)

        source = (
            filtered_df["Ad Source"]
            .fillna("Unknown")
            .value_counts()
            .reset_index()
        )

        source.columns = [
            "Ad Source",
            "Count"
        ]

        source["Source Group"] = "Other"

        # Direct Message
        source.loc[
            source["Ad Source"].eq("DM"),
            "Source Group"
        ] = "Direct Message"

        # Telegram
        source.loc[
            source["Ad Source"].str.contains(
                "telegram",
                case=False,
                na=False
            ),
            "Source Group"
        ] = "Telegram"

        # Facebook Ads
        source.loc[
            source["Ad Source"].str.contains(
                "ad_id",
                case=False,
                na=False
            ),
            "Source Group"
        ] = "Facebook Ads"

        # Australia Campaign
        source.loc[
            source["Ad Source"].str.contains(
                "AUST",
                case=False,
                na=False
            ),
            "Source Group"
        ] = "Australia Campaign"

        # Visa Campaign
        source.loc[
            source["Ad Source"].str.contains(
                "VF",
                case=False,
                na=False
            ),
            "Source Group"
        ] = "Visa Campaign"

        # USA Campaign
        source.loc[
            source["Ad Source"].str.contains(
                "USA",
                case=False,
                na=False
            ),
            "Source Group"
        ] = "USA Campaign"

        # Japan Campaign
        source.loc[
            source["Ad Source"].str.contains(
                "JP",
                case=False,
                na=False
            ),
            "Source Group"
        ] = "Japan Campaign"

        # Europe Campaign
        source.loc[
            source["Ad Source"].str.contains(
                "EU",
                case=False,
                na=False
            ),
            "Source Group"
        ] = "Europe Campaign"

        source = (
            source.groupby(
                "Source Group",
                as_index=False
            )
            .agg({"Count": "sum"})
            .sort_values(
                "Count",
                ascending=True
            )
        )

        fig = px.bar(
            source,
            x="Count",
            y="Source Group",
            orientation="h",
            text="Count",
            color="Count",
            color_continuous_scale="Oranges"
        )

        fig.update_traces(
            textposition="outside",
            textfont=dict(
                color="#6B7280",
                size=13
            )
        )
        max_count = source["Count"].max()

        fig.update_xaxes(
            range=[0, max_count * 1.25]
        )

        fig.update_layout(
            height=320,
            template="plotly_white",
            paper_bgcolor="white",
            plot_bgcolor="white",
            coloraxis_showscale=False,
            xaxis_title="Leads",
            yaxis_title="",
            font=dict(
                family="Inter",
                size=13,
                color="#1F2937"
            ),
            margin=dict(
                l=20,
                r=80,
                t=20,
                b=20
            )
        )

        st.plotly_chart(
            fig,
            width="stretch",
            config={
                "displayModeBar": False
            }
        )
