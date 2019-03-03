def a():
    def b():
        print("b")

    def c():
        print("c")
    b()
    c()


a()
