import ast
import pdb
import argparse
import z3

##################### BEGIN DESCRIPTION ###

# This file has lots of functions to create simple objects from a
# Python AST. Every function is documented, but functions that begin
# with a comment "AST Generation and Parsing" are not immediately
# relevant to your assignment.

# The programs you will analyze in this assignment contain an
# arbitrary nest of 'for' loops, followed by an index calculation for
# a memory read, and an index calculation for a memory write. It
# should be assumed that these accesses (the read and write) have the
# same base memory location. The indexes are calculated as an
# expression using integers and loop variables. All loops can be
# assumed to increment by 1 and have positive bounds. Please see the
# test cases for examples.

# Your assignment is to determine if it is safe to parallelize the
# outer-most loop. You should do this by testing if there is a
# possible conflict between the read and write indexes when executed
# by different threads. You will do this using an SMT solver, Z3.

# If you haven't please go through the Python Z3 tutorial at:
# https://ericpony.github.io/z3py-tutorial/guide-examples.htm
# You only need to go up to the "Functions" section after the
# "Machine Arithmetic" section.

# This assignment is a subset of what you would need to do in
# practice.  Specifically, you would also need to check write-write
# conflicts and have more base memory locations. Additionally, you
# might also choose to see if inner loops can be parallelized, even if
# the outer-most one can't. For this assignment, you only need to
# check the outer-most loop has a read-write conflict.

##################### END DESCRIPTION ###

# A class to represent a parsed For Loop.  Each For loop has an
# integer lower and upper bound and an associated variable It can be
# assumed to increment by 1. For example, all loops will look similar
# to:
#
# for k in range(5,50)
#
# will correspond to an object where lower bound is 5, upper bound is
# 50, and the variable is 'k'. Bounds will always be a single number
# or variable (not an expression).
#
# It can be assumed that outer loops will not reference any variables,
# but inner loops might reference outer loop variables. For example:
#
# for i in range(2,20):
#   for j in range(0,i):
#     ....
#
# is allowed.
class ForLoop:
    def __init__(self, lower_bound, upper_bound, variable):
        self.lb = lower_bound
        self.ub = upper_bound
        self.var = variable

    def get_upper_bound(self):
        return self.ub

    def get_lower_bound(self):
        return self.lb

    def get_variable_name(self):
        return self.var

# AST Generation and Parsing
#
# Given a python file, return an AST.
def get_ast_from_file(fname):
    f = open(fname, 'r')
    s = f.read()
    f.close()
    module_ast = ast.parse(s)
    body_ast = module_ast.body[0]    
    return body_ast

# AST Generation and Parsing
#
# Given a For node in the AST, create a ForLoop object
def get_loop_constraints(FOR_node):
    loop_var = FOR_node.target.id
    lower_bound = pp_expr(FOR_node.iter.args[0])
    upper_bound = pp_expr(FOR_node.iter.args[1])

    FL = ForLoop(lower_bound, upper_bound, loop_var)
    return FL

# AST Generation and Parsing
#
# Check for a variety of different Python AST nodes
def is_FOR_node(node):
    return str(node.__class__) == "<class '_ast.For'>"

def is_ReadIndex_node(node):
    return node.value.func.id == 'read_index'

def is_WriteIndex_node(node):
    return node.value.func.id == 'write_index'

def is_NAME_node(node):
    return str(node.__class__) == "<class '_ast.Name'>"

def is_NUM_node(node):
    return str(node.__class__) == "<class '_ast.Constant'>"

def is_MULT_node(node):
    return str(node.op.__class__) == "<class '_ast.Mult'>"

def is_ADD_node(node):
    return str(node.op.__class__) == "<class '_ast.Add'>"

# AST Generation and Parsing
#
# Given an expression node, return a pretty printed string,
# e.g. "((i + 5) * 6)"
def pp_expr(node):
    if is_NAME_node(node):
        return node.id
    if is_NUM_node(node):
        return str(node.n)
    if is_MULT_node(node):
        return "(" + pp_expr(node.left) + " * " + pp_expr(node.right) + ")"
    if is_ADD_node(node):
        return "(" + pp_expr(node.left) + " + " + pp_expr(node.right) + ")"
    assert(False)

# AST Generation and Parsing
#
# Given a top level node, return a list of ForLoops, a write_index
# expression string and a read_index expression string
def get_loops_and_index_strings(top_node):
    node_to_analyze = top_node
    for_loops = []
    while True:
        for_loops.append(get_loop_constraints(node_to_analyze))
        if (is_FOR_node(node_to_analyze.body[0])):
            node_to_analyze = node_to_analyze.body[0]
        else:
            break

    read_index = ""
    write_index = ""
    for expr in node_to_analyze.body:
        if is_ReadIndex_node(expr):
            read_index = pp_expr(expr.value.args[0])
        if is_WriteIndex_node(expr):
            write_index = pp_expr(expr.value.args[0])

    return for_loops, read_index, write_index

# This is the function that you will working mostly with for your
# assignment. It will determine if a write index and read index in a
# series of nested ForLoops may conflict if the outer loop is done in
# parallel. You should use the python wrapper for the Z3 SMT solver to
# determine if a series of constraints (corresponding to a confict) is
# satisfiable. 
#
# Arguments:
# for_loops: a list of ForLoops (see the top of the file for the class).
# The order of the ForLoops is the order of the nesting depth. You can
# assume that all variable names are single letters, e.g. i,j,k,m.
#
# read_index: a string represeting an expression that computes the
# index of the read access in the loop. The string will contain
# numbers, operators (*,+), and loop variables.
#
# write_index: same as read_index, except for with the index for the write
# access.
def check_parallel_safety(for_loops, read_index, write_index):

    smt_solver = z3.Solver()
    writer_vars = {}
    reader_vars = {}
    variables = []

    # My implementation created strings of equations using symbolic
    # z3 variables. I then used "eval" on these strings to create
    # z3 constraints.

    # For example, to constrain ix and iy not to be equal, I did
    # something like this:
    # eq = "ix != iy"
    # smt_solver.add(eval(eq))

    # You can iterate through the loops like so
    for i,f in enumerate(for_loops):
        # get loop elements
        loop_var = f.get_variable_name()
        lower_bound = f.get_lower_bound()
        upper_bound = f.get_upper_bound()

        # collect all loop vriables
        variables.append(loop_var)
        
        # create the reader loop variable for z3
        reader_var = z3.Int(loop_var + "0")
        # map loop variable name to reader loop variable
        # e.g. reader_vars["i"] = z3.Int("i0")
        reader_vars[loop_var] = reader_var
        # add constrains for the reader loop variable
        # if bounds are vriables, use the dict to get previous reader loop variables 
        smt_solver.add(reader_var >= reader_vars.get(lower_bound, lower_bound))
        smt_solver.add(reader_var < reader_vars.get(upper_bound, upper_bound))

        # create the writer loop variable for z3
        writer_var = z3.Int(loop_var + "1")
        # map loop variable name to writer loop variable
        # e.g. writer_vars['i'] = z3.Int("i1")
        writer_vars[loop_var] = writer_var
        # add constrains for the writer loop variable
        # if bounds are vriables, use the dict to get previous reader loop variables 
        smt_solver.add(writer_var >= writer_vars.get(lower_bound, lower_bound))
        smt_solver.add(writer_var < writer_vars.get(upper_bound, upper_bound))

        # the outest reader and writer loop variable have different values 
        if i == 0:
            smt_solver.add(reader_var != writer_var)
    
    # replace all variable names in index strings with z3 variables
    for loop_var in variables:
        # read_index uses reader loop variables
        read_index = read_index.replace(loop_var, "reader_vars[\"{}\"]".format(loop_var))
        # write_index uses writer loop variables
        write_index = write_index.replace(loop_var, "writer_vars[\"{}\"]".format(loop_var))

    # assume we have read-write conflicts
    smt_solver.add(eval(read_index + " == " + write_index))

    # After all the constraints are added, you check the formula
    # If the forula is sat, then there is some instance of loop variables
    # where the reader thread and writer thread can conflict, and thus it
    # is not safe to parallelize.    

    print(smt_solver)
    # if read-write conflicts are satisfiable, parallelism is not safe
    if smt_solver.check() == z3.sat:
        print(smt_solver.model())
        return False
    else:
        return True

# Top level function. Given a python file name, it parses the file,
# and analyzes it to determine if the top level for loop can be done
# in parallel.
#
# It returns True if it is safe to do the top loop in parallel,
# otherwise it returns False.
def analyze_file(fname):
    module_ast = get_ast_from_file(fname)
    for_loops, read_index, write_index = get_loops_and_index_strings(module_ast)
    return check_parallel_safety(for_loops, read_index, write_index)
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()   
    parser.add_argument('pythonfile', help ='The python file to be analyzed') 
    args = parser.parse_args()
    print(analyze_file(args.pythonfile))
