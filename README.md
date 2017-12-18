# PyExSMT
*Python Exploration with PySMT*

This code is a substantial rewrite of the PyExZ3 (https://github.com/thomasjball/PyExZ3) symbolic execution engine for Python, now using the PySMT project (https://github.com/pysmt/pysmt).

## Installing
```bash
# Install PySMT >= 0.7.1dev
git clone https://github.com/pysmt/pysmt.git
cd pysmt
python3 setup.py install # May need sudo
cd ..

# Install PyExSMT
git clone https://github.com/FedericoAureliano/PyExSMT.git
cd PyExSMT
python3 setup.py install # May need sudo
```

## Usage
```
usage: pyexsmt [-h] [--log LOGLEVEL] [--uninterp name return_type arg_types]
        [--entry ENTRY] [--graph] [--summary] [--max-iters MAX_ITERS]
        [--max-depth MAX_DEPTH] [--solver SOLVER]
        file
```

## Example

### [demo.py](/examples/demo.py)

```python
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
```

### Graph Generation

```bash
pyexsmt --graph demo.py
```

![demo graph](/images/demo.png)

```bash
pyexsmt --graph --uninterp lib int [int,int] demo.py
```

![demo graph](/images/demolib.png)

```bash
pyexsmt --graph --entry lib demo.py
```

![demo graph](/images/lib.png)

### Summary Generation

```
pyexsmt --summary demo.py

Summary:
((in1 = 0) ? ((in2 = 0) ? 0 : (in2 + in3)) : ((0 < (in1 + in2)) ? 0 : ((in2 = 0) ? 0 : (in2 + in3))))
```

```
pyexsmt --summary --uninterp lib int [int,int] demo.py

Summary:
((0 < lib(in1, in2)) ? 0 : lib(in2, in3))
```

```
pyexsmt --summary --entry lib demo.py

Summary:
((x = 0) ? 0 : (x + y))
```
