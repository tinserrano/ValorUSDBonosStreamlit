import streamlit as st

def footer():
    st.markdown(
        """
        <style>
        .footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: transparent;
            color: #808080;
            text-align: center;
            padding: 10px;
            font-size: 14px;
        }
        .footer a {
            color: #808080;
            text-decoration: none;
        }
        .footer a:hover {
            color: blue;
            text-decoration: underline;
        }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        <div class="footer">
        Creado en las 🏔️ por <a href="https://www.linkedin.com/in/martinepenas/" target="_blank">tinserrano</a>
        </div>
        """,
        unsafe_allow_html=True
    )