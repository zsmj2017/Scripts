#!/bin/bash

set -eu

THIS_SCRIPT_PATH=$(cd "$(dirname "$0")"; pwd)

cppLint() {
    echo "~~~ Start CppLint In $THIS_SCRIPT_PATH ~~~"
    cpplint --counting=detailed \
            --filter=-legal/copyright \
            --quiet \
            $( find $THIS_SCRIPT_PATH -name \*.h -or -name \*.c -or -name \*.cpp) \
            2>&1
    echo "~~~ CppLint Done ~~~"
}

cppLint

