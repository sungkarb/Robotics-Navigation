#!/bin/bash

# Activate the virtual environment
. robotics/bin/activate

# Install the required Python packages
pip install --upgrade pip
pip install -r requirements.txt