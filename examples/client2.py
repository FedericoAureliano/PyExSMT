def lib(x,y):
	return x > y

def client2(x,y):
	if(x or y):
		if lib(y,x):
			return x + y
	else:
		return lib(g(x,y),y)

def g(x,y):
	return x * y