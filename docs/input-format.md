# Assignment input format

Each nonblank line assigns one variable. Names start with an ASCII letter
or underscore and continue with ASCII letters, digits, or underscores.
The right side accepts a name, an unsigned integer or decimal, or two such
values joined by `+`, `-`, `*`, `/`, or `%`. Spaces are optional.

```text
sum = left + right
scaled = sum * 2.5
result = scaled
```

`left` and `right` are external inputs because the program never assigns them.
A name assigned anywhere in the program must be defined before its first read.
`a = a + 1` therefore needs an earlier assignment to `a`.

Comments, parentheses, negative literals, chained expressions, branches, and
loops are outside this grammar. Blank lines keep their original source numbers.
The parser accepts at most 100 assignments, 40 distinct names, 32 characters
per name, and 10,000 characters in total. The app reports a parsing error when
an input exceeds a bound.
