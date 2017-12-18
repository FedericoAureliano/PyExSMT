def lib(x,y):
    if x == 0:
        return 0
    else:
        return x + y
    return 10

def demo(in1, in2, in3):
    if lib(in1, in2) > 0:
        return 0
    else:
        return lib(in2, in3)