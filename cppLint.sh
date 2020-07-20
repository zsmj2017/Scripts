#!/bin/bash

set -eu

THIS_SCRIPT_PATH=$(cd "$(dirname "$0")"; pwd)

cppLint() {
    cppFiles=$(find $THIS_SCRIPT_PATH -name '*.h' -or -name '*.c' -or -name '*.cpp')
    # Without "", $cppFiles may be split out into multiple words
    # For more information, 
    # please see "https://stackoverflow.com/questions/13781216/meaning-of-too-many-arguments-error-from-if-square-brackets"
    if [ -z "$cppFiles" ];then
      echo "$THIS_SCRIPT_PATH has no cpp files!"
      exit
    fi
    cpplint --counting=detailed \
            --filter=-legal/copyright \
            --quiet \
            $cppFiles \
            2>$THIS_SCRIPT_PATH/cppLint_output.txt
}

cppLint

