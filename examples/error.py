def error(x):
    if x < 0:
        raise ValueError("OOPS!")
    else:
        return x