# -*- coding: utf-8 -*-
"""
Description:
    Implementation of the Streamlit app for the speech-to-text part of the project
"""
import streamlit as st
from audiorecorder import audiorecorder
from transformers import AutoModelForCTC, AutoProcessor, pipeline


def stt_main() -> str | None:
    """
    Main function for the speech-to-text part of the project

    Returns
    -------
    str
        Transcription of the audio file
    """
    st.title("🎙️ Audio Recorder")
    audio = audiorecorder("Click to record", "Click to stop")

    # device = get_device()
    processor = AutoProcessor.from_pretrained("florentinhaugwitz/wav2vec2_medical")
    model = AutoModelForCTC.from_pretrained("florentinhaugwitz/wav2vec2_medical")

    pipe = pipeline(
        "automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
    )

    if len(audio) > 0:
        audio_bytes = audio.tobytes()
        st.audio(audio_bytes)
        text = pipe(audio_bytes)
        st.subheader("Transcription")
        st.write("Text without spelling correction")
        st.write(text["text"])
        return text["text"]

    return None
