import io

s = io.StringIO()
s.write('abc')
s.write('de')

s = io.StringIO(s.getvalue())

# print(s.getvalue())

for l in s:
    print(l)
