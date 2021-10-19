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
    """ : [-5,3],

    # My cases:
    # Parenthesis and all the operations:
    """
    x = 2;
    y = 3;
    z = (x + y) * (x - y) / x ^ y;
    print(z);
    z = x + y * x - y / x ^ y;
    print(z);
    """ : [-0.625,7.625],

    # Associativity
    """
    x = 3 - 1 - 2;
    z = 2 ^ 3 ^ 2;
    print(x);
    print(z);
    """ : [0, 512],

    # Nested braces:
    """
    {}{}{{{}}}{}{}
    """ : [],

    # Global variables and local variables:
    """
    x = 1;
    print(x);
    {
        x = x + 2;
        print(x);
        {
            x = x + 3;
            print(x);
        }
        print(x);
    }
    print(x);
    """ : [1,3,6,3,1],

    # Floating point number and no trailing zeroes in the output:
    # Reference: Copied from the Q&A google document
    """
    x = 4.5 + 4.5;
    print(x);
    """ : [9]
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

    # My cases:
    # In C++ a lonely semicolon is legal. But allowing it is complicating and
    # the assignment does not require so. I leave it as an exception:
    """
    ;
    """,

    # Braces not matching:
    """
    {
        x = 1;
        {
            y = 2;
            {
                z = x / y;
                print(z);
        }
    }
    """

    # No leading and trailing zeros in the input:
    """
    x = 001;
    """,
    """
    x = 1.0;
    """,

    # 'print' is a reserved key word. Thank you Prof. Sorensen.
    """
    print = 1;
    """
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

    # My cases:
    # The assignment only requires exceptions in expressions
    # I also include them for prints
    """
    print(x);
    """,

    # Before the scope starts:
    """
    x = y;
    {
        y = 1;
    }
    """,

    # Between scopes:
    """
    {
        x = 1;
    }
        y = x;
    {
        x = 1;
    }

    """
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

