# -*- coding: utf-8 -*-
"""
Description:
    Implementation of the Streamlit app for the classification part of the project
"""
import os
import pickle

import pandas as pd
import streamlit as st
from imblearn.pipeline import Pipeline
from lime.lime_text import LimeTextExplainer

LR_MODEL_MASKED = os.path.join("models", "clf", "lr_model_masked.pkl")


def predict_probability(model: Pipeline, value: list[str]) -> pd.DataFrame:
    """
    get probabilities for sample

    Parameters
    ----------
    model : imblearn.pipeline.Pipeline
        best model from train.py
    value : list[str]
        sample

    Returns
    -------
    pd.DataFrame
        Probabilities for labels
    """

    prob_array = model.predict_proba(value)
    prob_df = (
        pd.DataFrame(prob_array, index=["Probability"], columns=model.classes_)
        .transpose()
        .sort_values(by="Probability", ascending=False)
    )
    return prob_df


def top_symptoms(model: Pipeline) -> pd.Series:
    """
    Get top symptoms for each class
    Parameters
    ----------
    model : imblearn.pipeline.Pipeline
        best model from train.py
    Returns
    -------
    pd.Series
        Top symptoms for each class
    """

    coef = model.named_steps["clf"].coef_
    vectorizer = model.named_steps["vect"]
    feat = vectorizer.get_feature_names_out()
    coef_df = pd.DataFrame(coef, columns=feat, index=model.classes_)
    top = coef_df.apply(lambda x: x.nlargest(5).index.tolist(), axis=1)
    return top


def lime_explainer(model: Pipeline, value: str) -> dict[str, list[tuple[str, float]]]:
    """
    Get features the model used for top predicted classes
    Parameters
    ----------
    model : imblearn.pipeline.Pipeline
        best model from train.py
    value : str
        sample
    Returns
    -------
    dict[str, list[tuple[str, float]]]
        Features from sample the model used to predict classes
    """
    explainer = LimeTextExplainer(class_names=model.classes_)
    num_features = len(value.split())
    exp = explainer.explain_instance(
        value,
        model.predict_proba,
        num_features=num_features,
        top_labels=3,
    )
    feat_importance = exp.as_map()
    feat_importance = {model.classes_[k]: v for k, v in feat_importance.items()}
    feat_importance = {
        k: [(value.split()[i], v) for i, v in v] for k, v in feat_importance.items()
    }
    feat_importance_pos = {
        k: [v for v in v if v[1] > 0] for k, v in feat_importance.items()
    }
    return feat_importance_pos


def get_words(
    x: str, feat_importance: dict[str, list[tuple[str, float]]]
) -> list[str] | None:
    """
    Get words from sample the model used to predict classes

    Parameters
    ----------
    x : str
        Name of class
    feat_importance : dict[str, list[tuple[str, float]]]
        Features from sample the model used to predict classes

    Returns
    -------
    list[str] | None
        Words from sample the model used to predict classes
    """
    if x in feat_importance:
        value = feat_importance[x]
        words = [v[0] for v in value]
        return words
    return None


def clf_main(str_clf: str) -> None:
    """
    Main function for the classification part of the project

    Parameters
    ----------
    str_clf : str
        String from nlp part of the project
    """

    st.title("Classification")
    # Load model
    model = pickle.load(open(LR_MODEL_MASKED, "rb"))

    prediction = predict_probability(model, [str_clf])
    prob1 = prediction["Probability"][0]
    prob2 = prediction["Probability"][1]
    prob3 = prediction["Probability"][2]

    # find the value of top_symptoms(model) where index is prediction.index[0]
    # only works for lr model
    top = top_symptoms(model)
    top_symptoms_1 = top[prediction.index[0]]
    top_symptoms_2 = top[prediction.index[1]]
    top_symptoms_3 = top[prediction.index[2]]

    # find the value of top symptoms from lime
    feat_importance = lime_explainer(model, str_clf)
    top_symptoms_1_lime = get_words(prediction.index[0], feat_importance)
    top_symptoms_2_lime = get_words(prediction.index[1], feat_importance)
    top_symptoms_3_lime = get_words(prediction.index[2], feat_importance)

    st.subheader(
        "Based on our algorithm you should consider contacting these departments"
    )
    with st.expander(prediction.index[0]):
        st.metric(
            label="Percentage of probability",
            value="{:.0%}".format(prob1),
        )
        st.write("Decision was based on these symptoms from your description:")
        st.write(top_symptoms_1_lime)
        st.write("Most relevant symptoms for this department in general:")
        st.write(top_symptoms_1)

    with st.expander(prediction.index[1]):
        st.metric(
            label="Percentage of probability",
            value="{:.0%}".format(prob2),
        )
        st.write("Decision was based on these symptoms from your description:")
        st.write(top_symptoms_2_lime)
        st.write("Most relevant symptoms for this department in general:")
        st.write(top_symptoms_2)

    with st.expander(prediction.index[2]):
        st.metric(
            label="Percentage of probability",
            value="{:.0%}".format(prob3),
        )
        st.write("Decision was based on these symptoms from your description:")
        st.write(top_symptoms_3_lime)
        st.write("Most relevant symptoms for this department in general:")
        st.write(top_symptoms_3)
