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

tokens = ["ID"] + list(reserved.values())

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

# You must implement all the production rules. Please review slides
# from Oct. 4 if you need a reference.

parser = yacc.yacc(debug=True)

def parse_string(s):
    global to_print
    global ST
    ST = SymbolTable()
    to_print = []
    parser.parse(s)
    return to_print
    
# Example on how to test locally in this file:
#parser.parse("""
#x = 5 + 4 * 5;
#i = 1 + 1 * 0;
#print(i);
#{
#  l = 5 ^ x;
#{
#    k = 5 + 7;
#}
#}
#q = x / i;
#print(q);
#""")

#for p in to_print:
#    print(p)
