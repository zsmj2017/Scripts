import os

class CppLintError:
    def __init__(self, cppLintLine):
        assert cppLintLine
        # location start from 1
        self.location = 0 
        self.category = ""
        self.description = ""
        # verbose:a number 0-5 to restrict errors to certain verbosity levels
        self.verbose = -1 
        self.parse(cppLintLine)

    def removeSquareBrackets(string):
        string = string.replace('[','')
        string = string.replace(']','')
        return string
    
    def parse(self, cppLintLine):
        (location, self.description, categoryAndVerbose) = cppLintLine.strip().split("  ")
        self.location = location.split(':')[1]
        categoryAndVerbose = CppLintError.removeSquareBrackets(categoryAndVerbose)
        self.category = categoryAndVerbose.split(' ')[0]
        self.verbose = categoryAndVerbose.split(' ')[1]
    
    def output(self):
        res = '\t'.join([self.location, self.category, self.description, self.verbose])
        return res

class CppLintFile:
    def __init__(self, filePath):
        assert filePath
        # store cpp files's path, will be needed in future
        self.path = filePath
        # extract file name
        self.fileName = os.path.basename(self.path).split('.')[0]
        self.errors = []
        self.content = []
       
    def parse(self):
        for line in self.content:
            self.errors.append(CppLintError(line))

    def addContent(self, strLine):
        assert strLine
        self.content.append(strLine)

    def output(self, path):
        TEXT_FILE_SUFFIX = '.txt'
        textFileName = ''.join([self.fileName, TEXT_FILE_SUFFIX])
        textFilePath = os.path.join(path, textFileName)
        with open(textFilePath, 'w') as fout:
            for error in self.errors:
                fout.write(''.join([error.output(),'\n']))
        
class Parser():
    def __init__(self):
        self.files = {}
        self.isParsed = False
        return
       
    def clear(self):
        self.files.clear()
        self.isParsed = False

    def parse(self, inputFile):
        self.clear()
        # read && store raw data
        with open(inputFile, 'r') as fin:
            lines = fin.readlines()
            for line in lines:
                fileName = line.split("  ")[0].split(":")[0]
                if fileName in self.files:
                    self.files[fileName].addContent(line)
                else:
                    self.files[fileName] = CppLintFile(fileName)
                    self.files[fileName].addContent(line)
        # real parse implementation           
        for lintFile in self.files.values():
            lintFile.parse()
        self.isParsed = True
        return

    def output(self, path):
        if not self.isParsed:
            print("Parse has not been performed")
            assert(False)
        for lintFile in self.files.values():
            lintFile.output(path)
        return