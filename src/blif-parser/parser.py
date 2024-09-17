from lark import Lark, Transformer, v_args
import itertools
import pprint

# Define the Transformer class
class CircuitTransformer(Transformer):
    def header(self, items):
        return {"header": items[0]}

    def model(self, items):
        return {"model": items[0]}

    def inputs(self, items):
        return {"inputs": list(items)}

    def outputs(self, items):
        return {"outputs": list(items)}

    def gate(self, items):
        gate_name = items[0]
        arguments = items[1].children
        return {"gate_name": gate_name, "arguments": arguments}

    def end(self, items):
        return {"end": ".end"}

    def argument(self, items):
        return items

    def input_list(self, items):
        return items

    def output_list(self, items):
        return items

    def IDENTIFIER(self, item):
        return str(item)

    def GATE_NAME(self, item):
        return str(item)

    def PATH(self, item):
        return str(item)

    def COMMENT(self, item):
        return str(item)

# Define the grammar
circuitGrammar = r"""
    start: header model inputs outputs gate+ end

    header: COMMENT
    model: ".model" PATH
    inputs: ".inputs" input_list
    outputs: ".outputs" output_list
    gate: ".gate" GATE_NAME arguments
    end: ".end"

    input_list: IDENTIFIER (IDENTIFIER)*
    output_list: IDENTIFIER (IDENTIFIER)*

    arguments: argument (argument)*
    argument: "a=" IDENTIFIER
            | "b=" IDENTIFIER
            | "O=" IDENTIFIER

    COMMENT: /#[^\n]*/
    PATH: /[a-zA-Z0-9\/_.-]+/
    IDENTIFIER: /[a-zA-Z0-9_]+/
    GATE_NAME: /[a-zA-Z0-9]+/

    %import common.WS
    %ignore WS


"""

class Statement():
    def __init__(self, gtype, name, inputList, output):
        self.gtype = gtype
        self.name = name
        self.inputList = inputList
        self.output = output

    def tostr(self):
        input_str = ', '.join(self.inputList)
        return f"Statement(Name: {self.name}, Type: {self.gtype}, Inputs: [{input_str}], Output: {self.output})"

    def __eq__(self, other):
        return self.output == other.output and self.inputList == other.inputList and self.gtype == other.gtype and self.name == other.name

    def __lt__(self, other):
        return self.compare(other) == -1

    def __gt__(self, other):
        return self.compare(other) == 1

    def compare(self, other):
        if self.output in other.inputList:
            return -1
        if other.output in self.inputList:
            return 1
        return 0

def insertItem(items, newItem, j):
    # Create a copy of the items
    itemsCpy = items.copy()

    # Handle the case when j is 0
    if j == 0:
        return [newItem] + itemsCpy

    # Handle the case when j is the length of the list
    if j == len(itemsCpy):
        return itemsCpy + [newItem]

    # Handle the general case
    return itemsCpy[:j] + [newItem] + itemsCpy[j:]

def insertStatement(newStatement, sortedStatements):
    for j in range(len(sortedStatements)):
        comparisonResult = newStatement.compare(sortedStatements[j])
        if comparisonResult == -1:
            sortedStatements = insertItem(sortedStatements, newStatement, j)
            return sortedStatements
        if comparisonResult == +1:
            pass
    sortedStatements.append(newStatement)
    return sortedStatements

def sortStatements(statements):
    sortedStatements = []
    for i in range(len(statements)):
        newStatement = statements[i]
        sortedStatements = insertStatement(newStatement = newStatement, sortedStatements = sortedStatements)
    return sortedStatements

class Parser():
    def __init__(self, moduleName="TestModule"):
        # Create the Lark parser
        self.larkParser = Lark(circuitGrammar, parser='lalr', transformer=CircuitTransformer())
        self.parseTree = None
        self.statementList = []
        self.wireList = []
        self.inputsList = []
        self.outputsList = []
        self.moduleName = moduleName

    def parse(self, inStr):
        self.parseTree = self.larkParser.parse(inStr)
        self.getStatementsList()
        self.statementList = sortStatements(self.statementList)
        self.getPortList()
        self.getWireList()

    def getWireList(self):
        for statement in self.statementList:
            if 'new' in statement.output:
                self.wireList.append(statement.output)

    def getStatementsList(self):
        i = 0
        for item in self.parseTree.children:
            if 'gate_name' in item.keys():
                gtype = item['gate_name']
                name = gtype + "_" + str(i)
                inputList = list(itertools.chain(*item['arguments'][:-1]))
                output = item['arguments'][-1][0]
                statement = Statement(gtype, name, inputList, output)
                self.statementList.append(statement)
                i += 1

    def getPortList(self):
        for item in self.parseTree.children:
            if 'inputs' in item.keys():
                self.inputsList = list(itertools.chain(*item['inputs']))
            if 'outputs' in item.keys():
                self.outputsList = list(itertools.chain(*item['outputs']))

    def getName(self):
        self.moduleName = self.parseTree['name']

    def printTree(self):
        pprint.pprint(self.parseTree)

    def extractListFromKey(self, objList, key):
        returnList = []
        for obj in objList:
            if obj['type'] == key:
                returnList.append(obj)
        return returnList

