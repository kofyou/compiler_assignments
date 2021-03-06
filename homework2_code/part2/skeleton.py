# skeleton file for UCSC CSE211 Homework 2: part 1

from pycfg.pycfg import PyCFG, CFGNode, slurp 
import argparse 
import re

# Acks: I used
# https://www.geeksforgeeks.org/draw-control-flow-graph-using-pycfg-python/
# to get started with PyCFG. 

# Given a node, returns the instruction as a string
# instructions are of the form:
def get_node_instruction(n):
    return n.attr["label"]

# Given a CFG and a node, return a list of successor nodes
def get_node_successors(CFG, n):
    return CFG.successors(n)

# given a node instruction string (e.g. from get_node_instruction),
# returns the name of the variable that is read (if any)
def reads_var(i):

    # matches "if" instructions of the form: <label>: if: <var>
    # returns <var> because it is a read variable
    if "if" in i:
        return re.match("\d+:\s*if:\s*(\S+)",i)[1]

    # matches "while" instructions of the form: <label>: while: <var>
    # returns <var> because it is a read variable
    if "while" in i:
        return re.match("\d+:\s*while:\s*(\S+)",i)[1]

    # inputs don't read any variable
    if "input" in i:
        return None

    # special nodes (start and stop) do not read anything
    if "start" in i or "stop" in i:
        return None

    # otherwise the instruction is an assignment of the form:
    # <label>: <var> = <var>
    # Returns the rhs variable
    assert("=" in i)
    return re.match("\d+:\s*(\S+)\s*=\s*(\S+)",i)[2]

# given a node instruction string (e.g. from get_node_instruction),
# returns the name of the variable that is written (if any)
def writes_var(i):

    # if statements in this subset don't write to any variables
    if "if" in i:
        return None

    # while loops in this subset don't write to any variables
    if "while" in i:
        return None

    # inputs write to the lhs variable
    if "input" in i:
        return re.match("\d+:\s*(\S+)\s*=\s*input\(\)",i)[1]

    # special nodes (start and stop) do not write to a variable
    if "start" in i or "stop" in i:
        return None

    # otherwise the instruction is an assignment of the form:
    # <label>: <var> = <var>
    # Returns the lhs variable
    assert("=" in i)
    return re.match("\d+:\s*(\S+)\s*=\s*(\S+)",i)[1]

# use PyCFG to get a CFG of the python input file.  Graph is returned
# as a PyGraphviz graph.  Don't worry too much about this function. It
# just uses the PyCFG API
def get_graph(input_file):
    cfg = PyCFG()
    cfg.gen_cfg(slurp(input_file).strip())
    arcs = []
    return CFGNode.to_graph(arcs)

# get the domain of all the variables. This is needed for the set
# compliment of VarKill in the iterative algorithm to compute LiveOut
def compute_VarDomain(CFG):

    # start with an empty set
    VarDomain = set({})

    # for each node in the CFG
    for n in CFG.nodes():

        # get the variables that are read from
        var1 = reads_var(get_node_instruction(n))

        # get the variables that are written to
        var2 = writes_var(get_node_instruction(n))

        # only add the variables if they are not None
        if var1 is not None:
            VarDomain = VarDomain.union(set([var1]))
        if var2 is not None:
            VarDomain = VarDomain.union(set([var2]))

    # return the final set
    return VarDomain

# get the UEVar set:
# hint: iterate over all the nodes and record only some of the variables
# used. Use reads_var and/or writes_var function to get variables

# Reference: The code style of my implementations, including but not
# limited to variable names and some structures like loops,
# mimics what has already been provided.
def compute_UEVar(CFG):
    UEVar = {}

    for n in CFG.nodes():

        # in a single instruction, the variable read is always read before written to
        var = reads_var(get_node_instruction(n))

        # initialize with a set containing the variable or an empty set
        if var is not None:
            UEVar[n] = set([var])
        else:
            UEVar[n] = set()

    return UEVar

# get the VarKill set:
# hint: iterate over all the nodes and record only some of the variables
# used. Use reads_var and/or writes_var function to get variables
def compute_VarKill(CFG):
    VarKill = {}

    for n in CFG.nodes():

        # the variable get written is killed
        var = writes_var(get_node_instruction(n))

        # initialize with a set containing the variable or an empty set
        if var is not None:
            VarKill[n] = set([var])
        else:
            VarKill[n] = set()

    return VarKill

# postorder: visit successors first
def postorder_traversal(CFG, n, visited, result):
    # mark as visited
    visited[n] = True
    for succ in get_node_successors(CFG, n):
        # visit the successor not visited yet
        if visited[succ] is False:
            # recursively visit the successor
            postorder_traversal(CFG, succ, visited, result)
    # visit the current node at last
    result.append(n)
    return

# which way to go
def get_traverse_order(mode, CFG):
    result = []
    visited = {n : False for n in CFG.nodes()}

    if mode == "PO":
        postorder_traversal(CFG, CFG.get_node(0), visited, result)
    elif mode == "RPO":
        postorder_traversal(CFG, CFG.get_node(0), visited, result)
        # reverse the PO order
        result.reverse()
    elif mode == "RPO on R":
        # traverse the reversed graph with postorder; should start with the new root
        postorder_traversal(CFG.reverse(), CFG.get_node(CFG.order() - 1), visited, result)
        # reverse the PO order
        result.reverse()
    else:
        result = CFG.nodes()

    return result

# iteratively compute LiveOut

# hint: this will be a fixed point iteration. It should look
# a lot like figure 8.14b in the EAC book.

# You can use get_node_successors(CFG, n) to get a list of n's
# successor nodes.
def compute_LiveOut(CFG, UEVar, VarKill, VarDomain):

    LiveOut = {}

    # all node start with an empty set
    for n in CFG.nodes():
        LiveOut[n] = set()

    # calculate order
    traverse_order = get_traverse_order("default", CFG)
    # print(traverse_order)
    # for n in traverse_order:
    #     print(n, get_node_instruction(n))

    # when will it converge?
    counter = 0
    # the flag for the fixed point algorithm
    changed = True
    while changed:
        counter += 1
        changed = False
        for n in traverse_order:
            # re-calculate the LiveOut set
            NodeLiveOut = set()
            # consider all information upflowed from successors
            for succ in get_node_successors(CFG, n):
                # upward exposed live variables: live varibles of succ that are not killed
                UELive = LiveOut[succ].intersection(VarDomain.difference(VarKill[succ]))
                # UEVar of succ also contributes
                NodeLiveOut = NodeLiveOut.union(UEVar[succ], UELive)

            # if LiveOut changes, the loop goes on
            if NodeLiveOut != LiveOut[n]:
                changed = True
                LiveOut[n] = NodeLiveOut

    print("converge after: ", counter)
    return LiveOut

# The uninitialized variables are the LiveOut variables from the start
# node. It is fine if your implementation needs to change this
# function. It simply needs to return a set of uninitialized variables
def get_uninitialized_variables_from_LiveOut(CFG, LiveOut):
    return LiveOut[CFG.get_node(0)]

# The testing function. Keep the signature of this function the
# same as it will be used for grading. I highly recommend you keep the
# function exactly the same and simply implement the constituent
# functions.
def find_undefined_variables(input_python_file):

    # Convert the python file into a CFG
    CFG = get_graph(input_python_file)

    # Get the variable domain (used to compute the VarKill set
    # compliment in the iterative algorithm)
    VarDomain = compute_VarDomain(CFG)

    # Get UEVar
    UEVar    = compute_UEVar(CFG)

    # Get VarKill
    VarKill  = compute_VarKill(CFG)

    # Get LiveOut
    LiveOut = compute_LiveOut(CFG, UEVar, VarKill, VarDomain)

    # Return a set of unintialized variables
    return get_uninitialized_variables_from_LiveOut(CFG, LiveOut)

# if you run this file, you can give it one of the python test cases
# in the test_cases/ directory.
# see solutions.py for what to expect for each test case.
if __name__ == '__main__': 
    parser = argparse.ArgumentParser()   
    parser.add_argument('pythonfile', help ='The python file to be analyzed') 
    args = parser.parse_args()
    print(find_undefined_variables(args.pythonfile))

# Observations:
# Rounds taken to converge for each traversal are listed as follows.
#
# In our context, the order PO and RPO on reversed graph produce indeed is different.
# The data structure stores the end note and it becomes the root node of the reversed graph.
# During RPO traversal on reversed graph, I think starting with the end node (the new
# root node) guarantees that the end node is the first one in the result, which is preferred
# in backwards flow analysis.
#
# In practice, among the cases provided, PO and RPO on the reversed graph make no difference.
# They both tend to start from the end, thus are more likely to take advantage of the LiveOut
# set of the end node.
#
# In contrast, RPO starts from the root and it converges slower. The defalut order and RPO
# makes a little difference. CFG.nodes() seems to always return the end node as the last in
# the list.
#
# | Test | Default | Reverse Post-Order | Post-Order | Reverse Post-Order on Reversed Graph |
# | :--: | :-----: | :----------------: | :--------: | :----------------------------------: |
# | 0.py |    2    |         2          |     2      |                  2                   |
# | 1.py |    5    |         5          |     2      |                  2                   |
# | 2.py |    5    |         5          |     2      |                  2                   |
# | 3.py |    6    |         6          |     3      |                  3                   |
# | 4.py |    7    |         7          |     3      |                  3                   |
# | 5.py |    6    |         6          |     3      |                  3                   |
# | 6.py |    8    |         9          |     3      |                  3                   |
# | 7.py |    8    |         8          |     3      |                  3                   |