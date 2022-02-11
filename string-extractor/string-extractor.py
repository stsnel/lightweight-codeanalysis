#!/usr/bin/env python3

import ast
import linecache
import re
import unittest

# Conditional constructions:
# - if [condition] <-- just pass condition to ast.parse
# - elif [condition] <-- just pass condition to ast.parse
# - var = a if [condition] else [b]

# Compound statements:
# - a or b or c
# - d or e or f
# - ( compound statements )
# - not g

# Terminal conditions
# a.startswith(string)
# b.endswith(string)
# c in string [fragment]
# d == string

# String formats
# - String literals
# - Format strings

class StringExtractor:
    def _preprocessLine(self, filename, lineNumber):
        """ Retrieves a line of code for parsing, checks whether it can be parsed
            and performs any transformations needed for dealing with control structures
            or multiline statements.
            
            Result is a 2-tuple, with the first element being a status code, and the second
            element being the preprocessed statement to be parsed.
            
            Status codes:
              OK           : line can be parsed
              NOTSUPPORTED : the parser should ignore this line, because the preprocessor
                             doesn't support this particular type of statement (in this context).
              ERROR        : the preprocessor was unable to transform the line into a
                             parsable form. This could happen for long multiline statements (length
                             more than maxMultilineLength), or for language constructs that aren't
                             recognized by the preprocessor.
            """
        maxMultilineLength= 20
        numberOfLines = self._getNumberOfLines(filename)
        line = linecache.getline(filename, lineNumber).strip()

        if filename.endswith(".j2"):
            return ("IGNORE","")
            
        # Ignore irrelevant control flow statements
        for keyword in ["try", "except", "finally", "else" ]:
            if re.match( "^{}\s*[\s:]$".format(keyword), line):
                return ("IGNORE", "")
        
        # Normalize elif statement to if statement.
        if re.match( "^elif\s", line):
            line = line[2:]

        # Check whether we are dealing with a relevant compound statement
        compoundStatement = False
        for keyword in ["for", "if", "while"]:
            if re.match( "^{}[\(\s]".format(keyword), line):
                compoundStatement = True

        statement = ""
        max_offset = max ( maxMultilineLength, numberOfLines - lineNumber )
        for offset in range(numberOfLines - lineNumber):
            thisLineNumber = lineNumber + offset

            if offset == 0:
                thisLine = line
            else:
                thisLine = linecache.getline(filename, thisLineNumber).strip()

            statement = " ".join([statement, thisLine ]).strip() 
            
            if statement.endswith("\\"):
                # Explicit line continuation. Keep iterating over lines,
                # even if maximum statement length has been exceeded.
                statement = statement[:-1]
                continue
            elif compoundStatement and statement.endswith(":"):
                # It seems we have a complete control structure statement.
                # Add a dummy block.
                statementWithDummyBlock = statement + "\n  pass"
                if self._isParsable(statementWithDummyBlock):
                    return ("OK", statementWithDummyBlock)

            elif (not compoundStatement) and self._isParsable(statement):
                return ("OK", statement)

            if offset >= maxMultilineLength:
                break

        return ("ERROR", "")


    def _isParsable(self, statement):
        """Determines whether a statement is parsable."""
        try:
            tree = ast.parse(statement)
            return True
        except SyntaxError:
            return False


    def _getNumberOfLines(self, filename):
        with open(filename, 'r') as file:
            for count, line in enumerate(file):
                pass
        return count + 1

    def getInterestingStrings(self, statement):
        tree = ast.parse(statement)
        collector = InterestingStringCollector()
        collector.visit(tree)
        return collector.getCollectedStrings() 


class InterestingStringCollector(ast.NodeVisitor):
    def __init__(self):
        self.suffixes = set()
        self.prefixes = set()
        self.fragments = set()
        self.fullStrings = set()


    def getCollectedStrings(self):
        return ( [ ( "SUFFIX", s ) for s in self.suffixes ] +
                 [ ( "PREFIX", s ) for s in self.prefixes ] +
                 [ ( "FRAGMENT", s ) for s in self.fragments ] +
                 [ ( "FULL", s ) for s in self.fullStrings ] )


    def visit_Compare(self, node):
        opstype = str(type(node.ops[0]))
        if opstype == "<class '_ast.Eq'>":
            leftClass = str(type(node.left))
            rightClass = str(type(node.comparators[0]))
            if leftClass == "<class '_ast.Str'>" and rightClass != "<class '_ast.Str'>":
                self.fullStrings.add(node.left.s)
            elif leftClass != "<class '_ast.Str'>" and rightClass == "<class '_ast.Str'>":
                self.fullStrings.add(node.comparators[0].s)
        elif opstype == "<class '_ast.In'>":
            leftClass = str(type(node.left))
            if leftClass == "<class '_ast.Str'>":
                self.fragments.add(node.left.s)


    def visit_Call(self,node):
        if node.func.attr == "startswith" and str(type(node.args[0])) == "<class '_ast.Str'>":
            self.prefixes.add(node.args[0].s)
        elif node.func.attr == "endswith" and str(type(node.args[0])) == "<class '_ast.Str'>":
            self.suffixes.add(node.args[0].s)
    

class TestStringExtractor(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.extractor = StringExtractor()


    def test_dummy(self):
        assert(True)

    def test_preprocess_jinja2(self):
        output = self.extractor._preprocessLine( "testfile_jinja.j2", 1)
        assert(output[0] == "IGNORE")

    def test_preprocess_one_line_statement(self):
        output = self.extractor._preprocessLine( "stringprocessor-testdata.py", 5)
        assert(output[0] == "OK")
        assert(output[1] == 'print("Hello")')

    def test_preprocess_two_line_statement_implicit(self):
        output = self.extractor._preprocessLine( "stringprocessor-testdata.py", 8)
        assert(output[0] == "OK")
        assert(output[1] == 'print( "Hello")')

    def test_preprocess_three_line_statement_implicit(self):
        output = self.extractor._preprocessLine( "stringprocessor-testdata.py", 12)
        assert(output[0] == "OK")
        assert(output[1] == 'print( "Hello" )')

    def test_preprocess_two_line_statement_explicit(self):
        output = self.extractor._preprocessLine( "stringprocessor-testdata.py", 17)
        assert(output[0] == "OK")
        assert(output[1] == 'print ("Hello")')

    def test_preprocess_three_line_statement_explicit(self):
        output = self.extractor._preprocessLine( "stringprocessor-testdata.py", 21)
        assert(output[0] == "OK")
        assert(output[1] == 'print ( "Hello")')

    def test_preprocess_if_statement(self):
        output = self.extractor._preprocessLine( "stringprocessor-testdata.py", 26)
        assert(output[0] == "OK")
        assert(output[1] == 'if foo == "bar":\n  pass')

    def test_preprocess_elif_statement(self):
        output = self.extractor._preprocessLine( "stringprocessor-testdata.py", 28)
        assert(output[0] == "OK")
        assert(output[1] == 'if foo == "baz":\n  pass')

    def test_comparison_equals_right(self):
        output = self.extractor.getInterestingStrings('a == "foo"')
        assert(len(output) == 1)
        assert(output[0][0] == "FULL")
        assert(output[0][1] == "foo")

    def test_comparison_equals_left(self):
        output = self.extractor.getInterestingStrings('"foo" == a')
        assert(len(output) == 1)
        assert(output[0][0] == "FULL")
        assert(output[0][1] == "foo")

    def test_comparison_in(self):
        output = self.extractor.getInterestingStrings('"foo" in a')
        assert(len(output) == 1)
        assert(output[0][0] == "FRAGMENT")
        assert(output[0][1] == "foo")

    def test_comparison_startswith(self):
        output = self.extractor.getInterestingStrings('a.startswith("foo")')
        assert(len(output) == 1)
        assert(output[0][0] == "PREFIX")
        assert(output[0][1] == "foo")

    def test_comparison_endswith(self):
        output = self.extractor.getInterestingStrings('a.endswith("foo")')
        assert(len(output) == 1)
        assert(output[0][0] == "SUFFIX")
        assert(output[0][1] == "foo")

# TODO: test ternary
# Test if, elif
# Test while

if __name__ == '__main__':
    unittest.main()
