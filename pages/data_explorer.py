import streamlit as st

def show_data_explorer(df):

    st.markdown("""
    <div class='page-title'>
    Data Explorer
    </div>
    """, unsafe_allow_html=True)

    st.dataframe(
        df,
        width="stretch"
    )