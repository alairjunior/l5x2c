# l5x2c

l5x2c is a [transcompiler](https://en.wikipedia.org/wiki/Source-to-source_compiler) (a source-to-source compiler) written in Python that translates Rockwell's ladder programs exported to a `.L5X` file into a C program with the purpose of verification. It is a **work-in-progress** and, as of now, it supports complex rung structure, the most used ladder instructions (see the [list](#supported-ladder-instructions)), tag definitions, multiple programs and routines.

l5x2c uses [PLY](http://www.dabeaz.com/ply/) to build a single pass transcompiler that translates the original ladder program into a C code that implements an [Accumulator Machine](https://en.wikipedia.org/wiki/Accumulator_(computing)) that models the behavior of the Rungs.


## Requirements

To run the Python Scripts, you are going to need [PLY](http://www.dabeaz.com/ply/). If you intend to run the l5x2c test script, you are going to need [CBMC](https://www.cprover.org/cbmc/). We are using CBMC version 5.11.

## Usage

There are 5 python scripts available in the repository:

* **l5x2c.py** is the main script and is used to translate the `.L5X` file into a C program
* **l5xparser.py** is the script that parses the `.L5X` file into a dictionary
* **runglex.py** is the scanner for the ladder rung. It analyses the rung and issues a stream of tokens
* **rungyacc.py** is the parser and code generator that analyses the sintax of the ladder rung and translates it to the equivalent C code
* **testgen.py** is a script that generate a C file that can be used to verify the behavior of *l5x2c*. The script generates a file `tests/tests.c` that can be verified using CBMC using the command `cbmc tests/tests.c`

To translate a `.L5X` file into C, just run:

```console
python l5x2c.py examples/ex1.L5X examples/ex1.c
```

This will analyse the file in `examples/ex1.L5X` and create the file `examples/ex1.c` with the corresponding C code.

Single ladder's rung can be translated using `rungyacc.py` as bellow:

```console
echo "XIC(A)XIO(B)OTE(C);" | python rungyacc.py
```

This will print a list of commands that use the template functions available in `plcmodel.template` file.

## Supported Ladder Instructions

The following instructions are supported by l5x2c:

* XIC
* XIO
* ONS
* EQU
* GEQ
* LEQ
* NEQ
* GRT
* LIM
* OTE
* OTU
* OTL
* RES
* MOV
* TON
* TOF
* CTU
* JSR
* ADD
* SUB
* DIV
* CLR
