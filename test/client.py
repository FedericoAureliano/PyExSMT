def lib(x,y):
	return x+y

def client(x,y):
	if(x or y):
		return lib(y,x)
	else:
		return lib(x,y)

