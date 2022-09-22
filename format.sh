#!/bin/bash

# Remove trailing whitespace from documentation files
# Format Python scripts using black

echo "Removing trailing whitespace..."
find . -name "*.md" -exec sed -i 's/[[:space:]]*$//' {} \;

echo "Formatting Python scripts..."
find . -name "*.py" -exec python3 -m black {} \+
