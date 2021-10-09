import ply.lex as lex

class SymbolTableException(Exception):
    pass

class ParsingException(Exception):
    pass

# Implement this class, i.e. provide some class members and implement
# the functions.
class SymbolTable:

    def __init__(self):
        self.dics = [{}]
    
    # check re-declaration
    def insert(self, name, value):
        if name in self.dics[-1]:
            #handle
            print("should update rather than insert\n")
            exit
        else:
            self.dics[-1][name] = value

    def update(self, name, value):
        for dic in reversed(self.dics):
            if name in dic:
                dic[name] = value
                return
        #handle
        print("should insert rather than update\n")
        exit

    # in case of 
    def lookup(self, name):
        for dic in reversed(self.dics):
            if name in dic:
                return dic[name]
        return None

    def push_scope(self):
        self.dics.append({})

    def pop_scope(self):
        if len(self.dics) > 1:
            self.dics.pop()

# I have provided you with the token rule to get ids and to get PRINT
# you must provide all other tokens
reserved = {
   'print' : 'PRINT'
}

tokens = ["ID", "INT", "FLOAT", "EQUAL", "PLUS", "MINUS", "MULT", "DIV", 
        "CARROT", "LPAR", "RPAR", "LBRA", "RBRA", "SEMI"] + list(reserved.values())

# token specification
t_INT = '0|[1-9][0-9]*'
t_FLOAT = '(0|[1-9][0-9]*)\.[0-9]*[1-9]'
t_EQUAL = '='
t_PLUS = '\+'
t_MINUS = '-'
t_MULT = '\*'
t_DIV = '/'
t_CARROT = '\^'
t_LPAR = '\('
t_RPAR = '\)'
t_LBRA = '{'
t_RBRA = '}'
t_SEMI = ';'
t_ignore = ' '

# token actions
def t_ID(t):
    "[a-zA-Z]+"
    t.type = reserved.get(t.value, 'ID')
    return t

# I have implemented the error function and newline rule for you
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    print("line number: %d" % t.lexer.lineno)
    raise ParsingException()

def t_newline(t):
    "\\n"
    t.lexer.lineno += 1

lexer = lex.lex()

#lexer.input("{haha = (3.1 / 2) ;} print(haha) ;")

#while True:
#    tok = lexer.token()
#    if not tok:
#        break
#    print(tok)

import ply.yacc as yacc

# Global variables I suggest you use (although you are not required)
to_print = []
ST = SymbolTable()

# I have implemented the parsing error function for you
def p_error(p):
    if p is not None:
        print("Syntax error in input on line: %d" % p.lineno)
    else:
        print("Syntax error in input")
    raise ParsingException()

# production rules
# You must implement all the production rules. Please review slides
# from Oct. 4 if you need a reference.

#def p_statements_braces(p):
#    "statements : lbra statements rbra"    

#def p_statements_recursive(p):
#    "statements : statement SEMI statements"

#def p_statements_empty(p):
#    "statements :"

# statements produces braces or statement recursion
def p_statements(p):
    """
    statements : lbra statements rbra statements
                | statement SEMI statements
                |
    """

# left brace '{' initiates an inner scope 
def p_lbra(p):
    "lbra : LBRA"
    ST.push_scope()

# right brace '{' ends a scope
def p_rbra(p):
    "rbra : RBRA"
    ST.pop_scope()

# print append value to list for future output
def p_statement_print(p):
    "statement : PRINT LPAR ID RPAR"
    to_print.append(ST.lookup(p[3]))

# assignment declares new variable
def p_statement_assignment(p):
    "statement : ID EQUAL expr"
    if ST.lookup(p[1]) is None:
        ST.insert(p[1], p[3])
    else:
        ST.update(p[1], p[3])

# following are rules encoded with precedence and associativity 
def p_expr(p):
    """
    expr : expr PLUS term
        | expr MINUS term
        | term
    """
    if len(p) == 2:
        p[0] = p[1]
    elif p[2] == '+':
        p[0] = p[1] + p[3]
    elif p[2] == '-':
        p[0] = p[1] - p[3]

# check divides by zero
def p_term(p):
    """
    term : term MULT pow
        | term DIV pow
        | pow
    """
    if len(p) == 2:
        p[0] = p[1]
    elif p[2] == '*':
        p[0] = p[1] * p[3]
    elif p[2] == '/':
        if p[3] == 0:
            #handle
            print("divided by zero")
            exit
        else:
            p[0] = p[1] / p[3]

def p_pow(p):
    """
    pow : factor CARROT pow
        | factor
    """
    if len(p) == 2:
        p[0] = p[1]
    elif p[2] == '^':
        p[0] = p[1] ** p[3]

def p_factor(p):
    """
    factor : LPAR expr RPAR
        | num
    """
    if len(p) == 2:
        p[0] = p[1]
    elif p[1] == '(':
        p[0] = p[2]

def p_num_int(p):
    "num : INT"
    p[0] = int(p[1])

def p_num_float(p):
    "num : FLOAT"
    p[0] = float(p[1])

# returns value of variable; check usage without declaration
def p_num_id(p):
    "num : ID"
    val = ST.lookup(p[1])
    if val is None:
        raise SymbolTableException()
    p[0] = val

parser = yacc.yacc(debug=True)

def parse_string(s):
    global to_print
    global ST
    ST = SymbolTable()
    to_print = []
    parser.parse(s)
    return to_print

# Example on how to test locally in this file:
parser.parse("""
x = 5 + 4 * 5;
i = 1 + 1 * 0;
print(i);
{
  l = 5 ^ x;
    {
        k = 5 + 7;
    }
}
q = x / i;
print(q);
""")

for p in to_print:
    print(p)
