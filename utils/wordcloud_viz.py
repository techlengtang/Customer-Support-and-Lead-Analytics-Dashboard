import pandas as pd
import plotly.express as px
import streamlit as st

from utils.nlp import _HAS_WORDCLOUD, WordCloud, build_word_frequencies, preprocess_text


def _build_wordcloud_image(clean_text, width=920, height=400):
    frequencies = dict(build_word_frequencies(clean_text, top_n=90))
    if not frequencies:
        return None

    cloud = WordCloud(
        width=width,
        height=height,
        background_color='#FFFFFF',
        colormap='Oranges',
        max_words=90,
        prefer_horizontal=0.82,
        min_font_size=14,
        max_font_size=96,
        margin=14,
        random_state=42,
    ).generate_from_frequencies(frequencies)

    return cloud.to_array()


def _keyword_bar_chart(keyword_df):
    fig = px.bar(
        keyword_df,
        x='Count',
        y='Keyword',
        orientation='h',
        color='Count',
        color_continuous_scale=['#FED7AA', '#FB923C', '#EA580C'],
        text='Count',
    )
    fig.update_traces(
        texttemplate='%{x}',
        textposition='outside',
        textfont=dict(size=11, color='#6B7280'),
        cliponaxis=False,
        marker_line_width=0,
    )
    fig.update_layout(
        height=max(320, 34 * len(keyword_df)),
        template='plotly_white',
        paper_bgcolor='white',
        plot_bgcolor='white',
        coloraxis_showscale=False,
        margin=dict(l=8, r=24, t=8, b=8),
        font=dict(family='Inter', size=12, color='#374151'),
        xaxis_title='',
        yaxis_title='',
    )
    fig.update_yaxes(categoryorder='total ascending')
    fig.update_xaxes(showgrid=True, gridcolor='#F3F4F6', zeroline=False)
    return fig


def render_objection_wordcloud_section(df, text_column='Quote_English'):
    """Render a styled word cloud with top keywords for objection quotes."""
    if text_column not in df.columns:
        return

    clean_text = (
        df[text_column]
        .dropna()
        .astype(str)
        .map(preprocess_text)
        .str.strip()
    )
    clean_text = clean_text[clean_text != '']

    if clean_text.empty:
        st.info('No objection text available for the word cloud.')
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
        f'Visual summary of the most common words across {len(clean_text):,} customer objection quotes.'
    )

    keywords = build_word_frequencies(clean_text, top_n=12)
    keyword_df = pd.DataFrame(keywords, columns=['Keyword', 'Count'])

    cloud_col, keywords_col = st.columns([1.45, 1], gap='large')

    with cloud_col:
        with st.container(border=True):
            if _HAS_WORDCLOUD:
                image = _build_wordcloud_image(clean_text)
                if image is not None:
                    st.image(image, use_container_width=True)
                else:
                    st.warning('Not enough text to generate a word cloud.')
            else:
                st.warning('Install the wordcloud package to render this visualization.')

    with keywords_col:
        with st.container(border=True):
            st.markdown(
                "<div class='wordcloud-sidecard-title'>Top Keywords</div>",
                unsafe_allow_html=True,
            )
            st.plotly_chart(
                _keyword_bar_chart(keyword_df),
                use_container_width=True,
                config={'displayModeBar': False},
            )

    st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)
