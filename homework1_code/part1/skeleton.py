import ply.lex as lex

class SymbolTableException(Exception):
    pass

class ParsingException(Exception):
    pass

# Implement this class, i.e. provide some class members and implement
# the functions.
class SymbolTable:

    def __init__(self):
        pass
    
    def insert(self,name,value):
        pass

    def lookup(self, name):
        pass
    
    def push_scope(self):
        pass

    def pop_scope(self):
        pass

# I have provided you with the token rule to get ids and to get PRINT
# you must provide all other tokens
reserved = {
   'print' : 'PRINT'
}

tokens = ["ID", "INT", "FLOAT", "EQUAL", "PLUS", "MINUS", "MULT", "DIV", 
        "EXP", "LPAR", "RPAR", "LBRA", "RBRA", "SEMI"] + list(reserved.values())

# token specification
t_INT = '0|[1-9][0-9]*'
t_FLOAT = '(0|[1-9][0-9]*).[0-9]*[1-9]'
t_EQUAL = '='
t_PLUS = '\+'
t_MINUS = '-'
t_MULT = '\*'
t_DIV = '/'
t_EXP = '\^'
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
def p_statements_braces(p):
    "statements : lbra statements rbra"

def p_statements_recursive(p):
    "statements : statement SEMI statements"

def p_statements_empty(p):
    "statements :"

def p_lbra(p):
    "lbra : LBRA"

def p_rbra(p):
    "rbra : RBRA"
    
def p_statement_print(p):
    "statement : PRINT LPAR ID RPAR"

def p_statement_assignment(p):
    "statement : ID EQUAL EXPR"


parser = yacc.yacc(debug=True)

def parse_string(s):
    global to_print
    global ST
    ST = SymbolTable()
    to_print = []
    parser.parse(s)
    return to_print

result = parser.parse("""
5 + 3;
""")
print(result)

# Example on how to test locally in this file:
#parser.parse("""
#x = 5 + 4 * 5;
#i = 1 + 1 * 0;
#print(i);
#{
#  l = 5 ^ x;
#    {
#        k = 5 + 7;
#    }
#}
#q = x / i;
#print(q);
#""")

#for p in to_print:
#    print(p)
