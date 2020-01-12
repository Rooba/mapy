class Foo:
    def __init__(self, a):
        self.a = a

foo = Foo(1)

a = {foo: 2}

print(a.get(foo))