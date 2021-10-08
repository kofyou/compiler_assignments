import skeleton as solution

valid_test_cases = {
    """
    x = 1 + 1;
    y = x + x;
    z = y ^ 2;
    print(z);
    """ : [16],
    
    """
    x = 1 + 2 * 10;
    y = (1+2) * 10;
    print(x);
    print(y);
    """ : [21,30],

    """
    x = 2 - 3 - 4;
    y = 2 - (3 - 4);
    print(x);
    print(y);
    """ : [-5,3]
}

parsing_error_test_cases = [
    """
    x = 1 ++ 1;
    """,
    
    """
    x5 = 1 + 2 * 10;
    """,

    """
    x = 2 - 3 - 4;
    y = 2 - (3 - 4)
    """,
]

symbol_table_error_test_cases = [
    """
    x = 1 + z;    
    """,
    
    """
    {
      x = 12 + 6;
    }
    z = x + x;
    """,

    """
    x = 62 + 78;
    {
       z = x + 1;
       {
         y = z + x;
       }
       w = y;
    }
    """,
]


for t in valid_test_cases:
    x = solution.parse_string(t)
    compare = valid_test_cases[t]
    for v in zip(x,compare):
        assert(str(v[0]) == str(v[1]))

for t in parsing_error_test_cases:
    try:
        solution.parse_string(t)
    except solution.ParsingException:
        pass
    else:
        assert(False)

for t in symbol_table_error_test_cases:
    try:
        solution.parse_string(t)
    except solution.SymbolTableException:
        pass
    else:
        assert(False)

