#!/bin/bash -e

scripts="$(git ls-files '*.sh')"
while IFS= read -r script
do
    echo "Validate $script"
    shellcheck "$script"
done <<< "$scripts"
