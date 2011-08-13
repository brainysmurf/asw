
def wow(func):
    print(dir(func))
    return func

class Thing:

    @wow
    def function(self, first, second):
        print(first, second, sep=", ")

if __name__ == '__main__':

    t = Thing()
    t.function("Hi", "Adam")
    t.function(['hi', 'there'], 'Adam')
