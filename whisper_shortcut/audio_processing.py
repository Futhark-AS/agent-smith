import logging
import os
import shutil
import traceback
import wave

import openai
import pyaudio
from config import Config
from pydub import AudioSegment
from pydub.silence import split_on_silence

logger = logging.getLogger()

def preprocess_audio(audio_file_name, raw_audio_file_name, min_silence_len=1000, silence_thresh=-45, pause_between_chunks=200):
    # Load the audio file
    audio = AudioSegment.from_wav(audio_file_name)

    old_length = len(audio)

    # Concatenate non-silent chunks to create the output audio
    output_audio = AudioSegment.empty()

    # Split the audio on silence
    chunks = split_on_silence(audio, min_silence_len=min_silence_len, silence_thresh=silence_thresh)

    # Add back a small silence in the places where silence was removed
    pause_segment = AudioSegment.silent(duration=pause_between_chunks)

    for i, chunk in enumerate(chunks):
        output_audio += chunk
        if i < len(chunks) - 1:
            output_audio += pause_segment

    new_length = len(output_audio)

    logger.info(f"Preprocessed audio file from {old_length}ms to {new_length}ms. ({(old_length - new_length) / old_length * 100:.2f}% reduction)")

    # Copy the raw audio to a new file
    shutil.copy(audio_file_name, raw_audio_file_name)

    # Save the output audio file
    output_audio.export(audio_file_name, format="wav")

def transcribe(audio_file_name, mode):
    audio_file = open(audio_file_name, "rb")
    logger.info("Transcribing audio...")
    if mode == "translate":
        transcript = openai.Audio.translate("whisper-1", audio_file)
    elif mode == "transcribe":
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
    else:
        logger.info("Invalid mode")
        return

    logger.info(f"Transcribed result: {transcript.text}")
    print(transcript)
    return transcript.text