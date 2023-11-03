class Test():
    def __init__(self):
        self.a = 1010

a = Test()
a.a = 10010
b = a.copy()
print(b.a)
b.a = 1001
print(a.a)