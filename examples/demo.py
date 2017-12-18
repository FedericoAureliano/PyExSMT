def lib(x,y):
    if x > y:
        return x
    else:
        return y

def demo(in1, in2, in3):
    if in1 == 0:
        if in2 == 5:
            return lib(in1, in2)
        else:
            if in3 <= 3:
                return 3
            else:
                return lib(in1, in2)
    else:
        if in1 == 1:
            if in2 == 7:
                return 5
            else:
                return 6
        else:
            return lib(in1, in2)
    return 0
