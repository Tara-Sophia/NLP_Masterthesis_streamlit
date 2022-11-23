# -*- coding: utf-8 -*-
"""
Description:
    Implementation of the Streamlit app for the nlp part of the project
"""
import streamlit as st


def nlp_main(str_nlp: str) -> str:
    """
    Main function for the nlp part of the project

    Parameters
    ----------
    str_nlp : str
        String to be processed

    Returns
    -------
    str
        Processed string
    """
    st.write("NLP")
    st.write(str_nlp)
    return str_nlp
