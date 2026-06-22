import streamlit as st
from pathlib import Path
from streamlit_option_menu import option_menu

from utils.paths import get_project_root, init_project_root

init_project_root(Path(__file__).resolve().parent)

from utils.load_data import load_data

from pages.dashboard import show_dashboard
from pages.data_explorer import show_data_explorer
from pages.objection_analysis import show_objection_analysis
from pages.lead_analytics import show_lead_analytics
from pages.sentiment_analysis import show_sentiment_analysis

st.set_page_config(
    page_title="Explorer Analytics",
    layout="wide",
    initial_sidebar_state="collapsed"
)
st.markdown("""
<link rel="stylesheet"
href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
""",
unsafe_allow_html=True)

with open(
    get_project_root() / "assets" / "style.css"
) as f:

    st.markdown(
        f"<style>{f.read()}</style>",
        unsafe_allow_html=True
    )

default_df = load_data()
df = st.session_state.get("dashboard_df", default_df)

with st.sidebar:
    st.image(str(get_project_root() / "assets" / "logo.png"), width=200)
    st.write("")

    selected = option_menu(
        menu_title=None,

        options=[
            "Dashboard",
            "Objection Analysis",
            "Lead Analytics",
            "Sentiment Analysis",
            "Data Explorer"
        ],

        icons=[
            "speedometer2",
            "exclamation-triangle",
            "people",
            "emoji-smile",
            "table"
        ],

        default_index=0,

        styles={
            "container": {
                "padding": "0!important",
                "background-color": "white"
            },

            "icon": {
                "color": "#FF8F5A",
                "font-size": "15px"
            },

            "nav-link": {
                "font-size": "15px",
                "font-weight": "500",
                "padding": "10px 14px",
                "border-radius": "10px",
                "margin": "4px 0",
                "--hover-color": "#FFF2EB"
            },

            "nav-link-selected": {
                "background-color": "#FF8F5A",
                "color": "white"
            }
        }
    )
if selected == "Dashboard":
    show_dashboard(df)

elif selected == "Objection Analysis":
    show_objection_analysis(df)

elif selected == "Lead Analytics":
    show_lead_analytics(df)

elif selected == "Sentiment Analysis":
    show_sentiment_analysis(df)

elif selected == "Data Explorer":
    show_data_explorer(df)
