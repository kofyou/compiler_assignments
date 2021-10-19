from skeleton import match_regex

tests = [("z?", "z", True),
         ("z?", "", True),
         ("z?", "y", False),
         ("z|y.x?", "", False),
         ("z|y.x?", "y", True),
         ("z|y.x?", "yx", True),
         ("z|y.x?", "z", True),
         ("e.x.c.i.t.e.(m.e.n.t)?", "excitement", True),
         ("e.x.c.i.t.e.(m.e.n.t)?", "excite", True),
         ("e.x.c.i.t.e.(m.e.n.t)? | c.a.r.s?", "excite", True),
         ("e.x.c.i.t.e.(m.e.n.t)? | c.a.r.s?", "excitement", True),
         ("e.x.c.i.t.e.(m.e.n.t)? | c.a.r.s?", "car", True),
         ("e.x.c.i.t.e.(m.e.n.t)? | c.a.r.s?", "cars", True),
         # My cases:
         ("a.l.l.(p.a.s.s.e.d|f.a.i.l.e.d)?", "all", True),
         ("a.l.l.(p.a.s.s.e.d|f.a.i.l.e.d)?", "allpassed", True),
         ("a.l.l.(p.a.s.s.e.d|f.a.i.l.e.d)?", "allfailed", True)]

failed = 0
total = len(tests)
for t in tests:
    result = match_regex(t[0], t[1])
    if result != t[2]:
        failed += 1
        print("--")
        print("failed: matching string " + t[1] + " to regex " + t[0])
        print("expected " + str(t[2]))
        print("got " + str(result))
        print("--")

print("total tests: " + str(total))
print("passed: " + str(total - failed))
print("failed: " + str(failed))
