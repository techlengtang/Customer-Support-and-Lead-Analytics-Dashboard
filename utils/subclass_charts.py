import json

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.nlp import apply_subclass_rules, preprocess_text, _resolve_rule_class_key
from utils.paths import get_config_path


def _load_subclass_rules():
    rules_path = get_config_path('subclass_rules.json')
    if not rules_path.exists():
        return None

    with open(rules_path, 'r', encoding='utf-8') as handle:
        return json.load(handle)


def get_subclass_summaries_from_df(
    df,
    text_column='Quote_English',
    label_column='Objection Type',
):
    """Assign rule-based subclasses and return per-class count summaries."""
    if df.empty or text_column not in df.columns or label_column not in df.columns:
        return None

    rules = _load_subclass_rules()
    if rules is None:
        return None

    working = df[[text_column, label_column]].dropna()
    if working.empty:
        return None

    texts = working[text_column].astype(str).map(preprocess_text)
    labels = working[label_column].astype(str)
    valid = texts.str.strip() != ''
    texts = texts.loc[valid]
    labels = labels.loc[valid]

    if texts.empty:
        return None

    result = apply_subclass_rules(texts.tolist(), labels.tolist(), rules)
    if result is None or result['assignments'].empty:
        return None

    return result


def _subclass_chart_figure(class_name, chart_df, total_quotes):
    chart_height = max(260, 44 * len(chart_df))
    fig = px.bar(
        chart_df,
        x='Count',
        y='Subclass',
        orientation='h',
        color='Count',
        color_continuous_scale='Oranges',
        text='Count',
        title=f'{class_name} ({total_quotes:,} quotes)',
    )
    fig.update_traces(
        texttemplate='%{x:,}',
        textposition='outside',
        textfont=dict(size=12, color='#6B7280', family='Inter'),
        cliponaxis=False,
    )
    fig.update_layout(
        height=chart_height,
        template='plotly_white',
        paper_bgcolor='white',
        plot_bgcolor='white',
        coloraxis_showscale=False,
        margin=dict(l=20, r=40, t=50, b=20),
        font=dict(family='Inter', size=13, color='#1F2937'),
        xaxis_title='Quotes',
        yaxis_title='',
        title=dict(font=dict(size=15, color='#1F2937')),
    )
    fig.update_yaxes(categoryorder='total ascending')
    return fig


def render_objection_class_overview(df, label_column='Objection Type'):
    """Render a high-level chart of all objection classes before subclass drill-down."""
    if df.empty or label_column not in df.columns:
        return

    class_counts = (
        df[label_column]
        .dropna()
        .astype(str)
        .value_counts()
        .reset_index()
    )
    class_counts.columns = ['Objection Class', 'Quotes']
    class_counts['Share'] = (
        class_counts['Quotes'] / class_counts['Quotes'].sum() * 100
    ).round(1)
    class_counts['Share'] = class_counts['Share'].apply(lambda x: f"{x:.1f}%")

    st.markdown(
        """
        <div class='chart-title'>
            Objection Class Overview
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(
        'Start here to see how customer quotes are distributed across all main objection classes.'
    )

    bar_col, pie_col = st.columns([1.55, 1], gap='large')

    with bar_col:
        bar_fig = px.bar(
            class_counts.sort_values('Quotes', ascending=True),
            x='Quotes',
            y='Objection Class',
            orientation='h',
            color='Quotes',
            color_continuous_scale='Oranges',
            text='Quotes',
        )
        bar_fig.update_traces(
            texttemplate='%{x:,}',
            textposition='outside',
            textfont=dict(size=12, color='#6B7280', family='Inter'),
            cliponaxis=False,
        )
        bar_fig.update_layout(
            height=max(360, 42 * len(class_counts)),
            template='plotly_white',
            paper_bgcolor='white',
            plot_bgcolor='white',
            coloraxis_showscale=False,
            margin=dict(l=20, r=40, t=10, b=20),
            font=dict(family='Inter', size=13, color='#1F2937'),
            xaxis_title='Quotes',
            yaxis_title='',
        )
        bar_fig.update_xaxes(showgrid=True, gridcolor='#F3F4F6', zeroline=False)
        st.plotly_chart(bar_fig, use_container_width=True, config={'displayModeBar': False})

    with pie_col:
        pie_fig = px.pie(
            class_counts,
            names='Objection Class',
            values='Quotes',
            hole=0.58,
            color_discrete_sequence=px.colors.sequential.Oranges_r,
        )
        pie_fig.update_traces(
            textinfo='percent',
            textposition='outside',
            textfont=dict(size=11, family='Inter'),
            marker=dict(line=dict(color='white', width=2)),
        )
        pie_fig.update_layout(
            height=max(360, 42 * len(class_counts)),
            template='plotly_white',
            paper_bgcolor='white',
            plot_bgcolor='white',
            margin=dict(l=10, r=10, t=10, b=10),
            font=dict(family='Inter', size=12, color='#374151'),
            showlegend=False,
        )
        st.plotly_chart(pie_fig, use_container_width=True, config={'displayModeBar': False})
    table_df = class_counts.rename(columns={'Share': 'Share (%)'})

    row_template = (
        '<tr>'
        '<td style="text-align:left; padding:10px 16px;">{cls}</td>'
        '<td style="text-align:center; padding:10px 16px;">{quotes:,}</td>'
        '<td style="text-align:center; padding:10px 16px;">{share}</td>'
        '</tr>'
    )
    rows_html = ''.join(
        row_template.format(
            cls=row['Objection Class'],
            quotes=row['Quotes'],
            share=row['Share (%)'],
        )
        for _, row in table_df.iterrows()
    )

    table_html = (
        '<table style="width:100%; border-collapse:collapse; font-family:Inter, sans-serif; font-size:14px;">'
        '<thead><tr style="background:#F8FAFC; color:#64748B;">'
        '<th style="text-align:left; padding:10px 16px; font-weight:500;">Objection Class</th>'
        '<th style="text-align:center; padding:10px 16px; font-weight:500;">Quotes</th>'
        '<th style="text-align:center; padding:10px 16px; font-weight:500;">Share (%)</th>'
        '</tr></thead>'
        f'<tbody>{rows_html}</tbody>'
        '</table>'
    )

    st.markdown(table_html, unsafe_allow_html=True)
    st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)

CLUSTER_CLASS_STYLES = {    
        'Documentation': 'cluster-card-documentation',
        'Trust': 'cluster-card-trust',
        'Competitor Comparison': 'cluster-card-competitor',
        'Lack of Understanding': 'cluster-card-understanding',
        'Location': 'cluster-card-location',
        'Price': 'cluster-card-price',
        'Processing Time': 'cluster-card-processing',
        'Risk / Guarantee Concerns': 'cluster-card-risk',
    }


def _taxonomy_summary(rules):
    classes = rules.get('classes', {})
    total_clusters = sum(len(info.get('subclasses', {})) for info in classes.values())
    return len(classes), total_clusters, classes


def render_cluster_catalog():
    """Display the canonical 8 objection types and 31 cluster names."""
    rules = _load_subclass_rules()
    if rules is None:
        return

    class_count, cluster_count, classes = _taxonomy_summary(rules)

    st.markdown(
        """
        <div class='chart-title'>
            Customer Objections and Corresponding Clusters
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(
        f'{class_count} objection types and {cluster_count} unique objection/cluster pairs '
        'from the customer objection taxonomy.'
    )

    class_order = list(CLUSTER_CLASS_STYLES.keys())
    ordered_classes = [name for name in class_order if name in classes]
    ordered_classes.extend(name for name in classes if name not in ordered_classes)

    for class_name in ordered_classes:
        subclasses = list(classes[class_name].get('subclasses', {}).keys())
        style_class = CLUSTER_CLASS_STYLES.get(class_name, 'cluster-card-default')
        chips = ''.join(
            f'<span class="cluster-chip">{name}</span>'
            for name in subclasses
        )
        st.markdown(
            f"""
            <div class="cluster-card {style_class}">
                <div class="cluster-card-header">
                    <span class="cluster-card-title">{class_name}</span>
                    <span class="cluster-card-count">{len(subclasses)} clusters</span>
                </div>
                <div class="cluster-chip-row">{chips}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.caption(
        'Note: labels are shown once per unique objection/cluster pair from the full customer objection dataset.'
    )
    st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)


def _complete_class_summary(class_name, items, rules):
    """Ensure every official cluster name appears, even when count is zero."""
    rule_classes = rules.get('classes', {})
    rule_key = _resolve_rule_class_key(class_name, list(rule_classes.keys()))
    if not rule_key or rule_key not in rule_classes:
        return [item for item in items if item.get('subclass') != 'Unspecified']

    official_names = list(rule_classes[rule_key].get('subclasses', {}).keys())
    counts = {item['subclass']: item['count'] for item in items}
    return [{'subclass': name, 'count': counts.get(name, 0)} for name in official_names]


def render_all_subclass_charts(summary, columns=2, show_section_header=True):
    """Render one bar chart per objection class showing subclass counts."""
    if not summary:
        st.info('No subclass data available.')
        return

    if show_section_header:
        st.markdown(
            """
            <div class='chart-title'>
                Subclass Breakdown by Objection Class
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption(
            'Each chart shows quote counts for the official objection clusters within that class.'
        )

    rules = _load_subclass_rules()
    rule_classes = set(rules.get('classes', {}).keys()) if rules else set()
    class_names = [
        name for name in summary.keys()
        if _resolve_rule_class_key(name, list(rule_classes)) in rule_classes
    ]
    class_names = sorted(
        class_names,
        key=lambda name: sum(item['count'] for item in summary[name]),
        reverse=True,
    )
    chart_cols = st.columns(columns)

    for index, class_name in enumerate(class_names):
        items = _complete_class_summary(class_name, summary[class_name], rules)
        chart_df = pd.DataFrame(items).rename(columns={'subclass': 'Subclass', 'count': 'Count'})
        chart_df = chart_df[chart_df['Count'] > 0]
        if chart_df.empty:
            continue
        total_quotes = int(chart_df['Count'].sum())

        with chart_cols[index % columns]:
            fig = _subclass_chart_figure(class_name, chart_df, total_quotes)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
