tokens0 = ''
tokens0_1 = '    '
tokens0_3 = '  \n  '
tokens1 = 'level0'
tokens2 = 'level0\ntokens1'
tokens3 = """level0
  level1
"""
tokens4 = """level0
 level1
 level1
"""
tokens5 = """level0
    level1
        level2
"""
tokens6 = """level0
    level1
        level2
        level2
"""
tokens7 = """level0
    level1
        level2
         level3
"""
tokens8 = """level0
    level1
        level2
level0
"""
tokens9 = """level0
    level1

        level2
level0
"""

tokens10 = """level0
    level1


        level2
level0
"""

tokens11 = """level0
    level1


      level2

level0
"""

t1 = """- t
n
p:
"""

t1_expected = """t
n
p
e"""

t1_1 = """p:
    - t"""

t2 = """
p1:
    - t1
        n1
        n2
    - t2
        - t3
p2:
    - t4
""".strip()

t2_expected = """
p
 t
  n
  n
 t
  t
p
 t
""".strip()

t3 = """
p:
    - t1

    - t2
""".strip()

t3_expected = """
p
 t
 e
 t
""".strip()

t4 = """
- t1
- t2
n
n
p:
    - t3

        - t4
""".strip()

t4_expected = """
t
t
n
n
p
 t
  e
  t
""".strip()

t5 = """
- t1
- t2
n
n
p::
    - t3

        - t4
""".strip()


t5_expected = """
t
t
n
n
p
 t
  e
  t
""".strip()

f1 = """p:
    - y
        - x
        - z
"""
word_x = 'x'
f1__word_x = """p:
    - y
        - x"""
