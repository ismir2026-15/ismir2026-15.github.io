#!/usr/bin/env bash

# Name of the output directory where we put the reorganized structure
OUTPUT_DIR="restructured"

# Create the output directory (if not already present)
mkdir -p "$OUTPUT_DIR"

# Iterate over each item in the current directory
for experiment in */; do
    # Skip if it's not a directory
    [ -d "$experiment" ] || continue

    # Also skip if it's our new OUTPUT_DIR (we don't want to recurse into our new structure)
    if [ "$experiment" = "$OUTPUT_DIR/" ]; then
        continue
    fi

    # Extract just the experiment name (strip trailing slash)
    exp_name=$(basename "$experiment")

    # Create the corresponding experiment directory in OUTPUT_DIR
    mkdir -p "$OUTPUT_DIR/$exp_name"

    # Iterate over each model folder in this experiment
    for model in "$experiment"*/; do
        [ -d "$model" ] || continue

        # Get the model name (e.g. "flow", "model_1", etc.)
        model_name=$(basename "$model")

        # Iterate over each sample folder in this model
        for sample in "$model"*/; do
            [ -d "$sample" ] || continue

            # Get the sample name (e.g. "sample_1")
            sample_name=$(basename "$sample")

            # Create a place for this sample in the new structure
            mkdir -p "$OUTPUT_DIR/$exp_name/$sample_name"

            # If the model is "flow", copy target.wav as ground_truth.wav
            if [ "$model_name" = "flow" ]; then
                if [ -f "$sample/target.wav" ]; then
                    cp "$sample/target.wav" "$OUTPUT_DIR/$exp_name/$sample_name/ground_truth.wav"
                fi
            fi
            # Otherwise, copy pred.wav as model_name.wav
            if [ -f "$sample/pred.wav" ]; then
                cp "$sample/pred.wav" "$OUTPUT_DIR/$exp_name/$sample_name/${model_name}.wav"
            fi
        done
    done
done
