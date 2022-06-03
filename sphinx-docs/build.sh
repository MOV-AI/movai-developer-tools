#!/bin/bash

# Install build requirements
pip3 install -r ./build-requirements.txt
# Auto-generate the rst Files
sphinx-apidoc -f -o ./source ../movai_developer_tools
# Build the HTML
make -C . html
# Copy html files to docs/
echo "Copying html files from build/html/ to docs/"
cp -R ./build/html/* ../docs/