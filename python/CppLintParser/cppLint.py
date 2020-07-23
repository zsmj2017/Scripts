import os
import subprocess
import argparse
from cppLintParser import Parser


def parseArgs():
    argParser = argparse.ArgumentParser(description="Process cpplint output")
    argParser.add_argument('-wd', dest='wd', help='Cpp Project Path')
    argParser.add_argument('-sh', dest='script', help='CppLint.sh\'s Path')
    argParser.add_argument(
        '-in', dest='input', help='CppLintParser\'s input file')
    argParser.add_argument('-o', dest='output', help='CppLint File Output Path')
    args = argParser.parse_args()
    return args


def runShellScript(shellScript):
    if os.path.exists(shellScript):
        subprocess.Popen(shellScript, shell=True)
    else:
        print("Here is no %s !" % (shellScript))
        assert False


def processShellScriptOuput(inputFile, outPutPath):
    if os.path.exists(inputFile):
        cppLintparser = Parser()
        cppLintparser.parse(inputFile)
        if not os.path.exists(outPutPath):
            os.makedirs(outPutPath)
        cppLintparser.output(outPutPath)
    else:
        print("Here is no %s !" % (inputFile))
        assert False


if __name__ == '__main__':
    args = parseArgs()
    runShellScript(args.script)
    processShellScriptOuput(args.input, args.output)
