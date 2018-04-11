from pyexsmt.symbolic_types.symbolic_int import create_shadow

def andor_shadow(x,y):
	x = create_shadow(x, x+1) #New version x = x, old version x = x+1
	if((create_shadow(x, x-1) or (create_shadow(y, x > y)))): #New version if (x or y), old version if ((x-1) or x>y)
		return 1
	else:
		return 2

