# PyExSMT
*Python Exploration with PySMT*

This code is a substantial rewrite of the PyExZ3 (https://github.com/thomasjball/PyExZ3) symbolic execution engine for Python, now using the PySMT project (https://github.com/pysmt/pysmt).

## Installing
    git clone git@github.com:FedericoAureliano/PyExSMT.git
    cd PyExSMT
    git clone git@github.com:pysmt/pysmt.git
    cd pysmt
    python3 setup.py install
    cd ..
    python3 setup.py install

## Usage
    usage: pyexsmt [-h] [--log LOGLEVEL] [--uninterp name return_type arg_types]
               [--entry ENTRY] [--graph] [--summary] [--max-iters MAX_ITERS]
               [--max-depth MAX_DEPTH] [--solver SOLVER]
               file

    positional arguments:
    file                  Select Python file

    optional arguments:
    -h, --help            show this help message and exit
    --log LOGLEVEL        Set log level
    --uninterp name return_type arg_types 
                          <func_name> <return_type> <arg_types>
    --entry ENTRY         Specify entry point
    --graph               Generate a DOT graph of execution tree
    --summary             Generate a functional summary
    --max-iters MAX_ITERS
                          Limit number of iterations
    --max-depth MAX_DEPTH
                          Limit the depth of paths
    --solver SOLVER       Choose SMT solver

## Examples

```
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
```

    pyexsmt --graph examples/demo.py
![demo graph](/images/demo.png)

    pyexsmt --graph examples/demo.py --uninterp lib int [int,int]
![demo graph](/images/demolib.png)

    pyexsmt --summary examples/demo.py --uninterp lib int [int,int]

    Summary:
    ((in1 = 0) ? ((in2 = 5) ? lib(in1, in2) : ((in3 <= 3) ? 3 : lib(in1, in2))) : ((in1 = 1) ? ((in2 = 7) ? 5 : 6) : lib(in1, in2)))