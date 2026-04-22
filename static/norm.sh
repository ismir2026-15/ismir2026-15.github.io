#!/usr/bin/env bash

# Directory containing the reorganized structure
BASE_DIR="restructured"

# Use `find` to locate all .wav files under BASE_DIR
find "$BASE_DIR" -type f -name '*.wav' | while read -r wav_file; do
    
    echo "Normalizing: $wav_file"
    
    # Normalize in place via SoX:
    #  1. Create a temporary normalized file (normalized.wav).
    #  2. Move it back to the original location.
    # ffmpeg -i "$wav_file" -af loudnorm normalized.wav
    sox "$wav_file" normalized.wav norm -1.0
    mv -f normalized.wav "$wav_file"

done

echo "All .wav files under '$BASE_DIR' have been normalized."
