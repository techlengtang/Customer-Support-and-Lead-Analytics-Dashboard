import pandas as pd
import plotly.express as px
import streamlit as st

from utils.nlp import (
    _HAS_WORDCLOUD,
    WordCloud,
    build_word_frequencies,
    preprocess_text,
)


WORDCLOUD_CHART_HEIGHT = 520
KEYWORD_CHART_HEIGHT = 380
WORDCLOUD_IMAGE_WIDTH = 1400
WORDCLOUD_IMAGE_HEIGHT = 1040


def _build_wordcloud_image(clean_text, width=1400, height=1040):

    frequencies = dict(
        build_word_frequencies(
            clean_text,
            top_n=80
        )
    )

    if not frequencies:
        return None

    cloud = WordCloud(
        width=width,
        height=height,
        background_color="white",
        colormap="Oranges",
        max_words=80,
        prefer_horizontal=0.9,
        min_font_size=18,
        max_font_size=150,
        margin=6,
        random_state=42,
    ).generate_from_frequencies(frequencies)

    return cloud.to_array()


def _keyword_bar_chart(keyword_df):

    fig = px.bar(
        keyword_df,
        x="Count",
        y="Keyword",
        orientation="h",
        color="Count",
        text="Count",
        color_continuous_scale=[
            "#FED7AA",
            "#FB923C",
            "#EA580C"
        ],
    )

    fig.update_traces(
        texttemplate="%{x}",
        textposition="outside",
        cliponaxis=False,
        marker_line_width=0,
    )

    fig.update_layout(
        height=KEYWORD_CHART_HEIGHT,
        autosize=False,
        template="plotly_white",
        paper_bgcolor="white",
        plot_bgcolor="white",
        coloraxis_showscale=False,
        margin=dict(
            l=20,
            r=50,
            t=5,
            b=5
        ),
        xaxis_title="",
        yaxis_title="",
        font=dict(
            size=13
        ),
    )

    fig.update_yaxes(
        categoryorder="total ascending"
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor="#F3F4F6"
    )

    return fig


def render_objection_wordcloud_section(
    df,
    text_column="Quote_English"
):

    if text_column not in df.columns:
        return

    clean_text = (
        df[text_column]
        .dropna()
        .astype(str)
        .map(preprocess_text)
        .str.strip()
    )

    clean_text = clean_text[clean_text != ""]

    if clean_text.empty:
        st.info("No objection text available.")
        return

    st.markdown(
        """
        <div class='chart-title'>
            Objection Language at a Glance
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption(
        f"Visual summary of the most common words across {len(clean_text):,} customer objection quotes."
    )

    keywords = build_word_frequencies(
        clean_text,
        top_n=12
    )

    keyword_df = pd.DataFrame(
        keywords,
        columns=[
            "Keyword",
            "Count"
        ]
    )

    left, right = st.columns(2)

    with left:

        st.markdown(
            """
            <div class='chart-title'>
                Word Cloud
            </div>
            """,
            unsafe_allow_html=True,
        )

        if _HAS_WORDCLOUD:

            image = _build_wordcloud_image(
                clean_text,
                width=WORDCLOUD_IMAGE_WIDTH,
                height=WORDCLOUD_IMAGE_HEIGHT
            )

            if image is not None:

                fig = px.imshow(image)

                fig.update_layout(
                    height=KEYWORD_CHART_HEIGHT,
                    margin=dict(l=0, r=0, t=0, b=0),
                    paper_bgcolor="white",
                    plot_bgcolor="white",
                )

                fig.update_xaxes(visible=False)
                fig.update_yaxes(visible=False)

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    config={"displayModeBar": False}
                )

            else:

                st.warning(
                    "Not enough text to generate word cloud."
                )

        else:

            st.warning(
                "Install wordcloud package."
            )

    with right:

        st.markdown(
            """
            <div class='chart-title'>
                Top Keywords
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.plotly_chart(
            _keyword_bar_chart(keyword_df),
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )

    st.markdown("<br>", unsafe_allow_html=True)
