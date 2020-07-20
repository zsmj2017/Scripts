#!/bin/bash

set -eu

THIS_SCRIPT_PATH=$(cd "$(dirname "$0")"; pwd)
CLANG_FORMAT_CONG_FILE=".clang-format"

# Check whether the .clang-format file exists in current path
if [ ! -f $CLANG_FORMAT_CONG_FILE ];then
	echo "$THIS_SCRIPT_PATH Has No .clang-format!"
	exit 
fi

format() {
	echo "~~~ Start Code Format In $THIS_SCRIPT_PATH ~~~"
    for f in $(find $THIS_SCRIPT_PATH -name '*.h' -or -name '*.c' -or -name '*.cpp'); do 
        echo "format ${f}"
        clang-format -i -style=file ${f}
    done
    echo "~~~ Code Format Done ~~~"
}

format

