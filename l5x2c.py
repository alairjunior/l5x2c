#!/usr/bin/python
# -*- coding: utf-8 -*-
################################################################################
# Copyright (c) 2019 Alair Dias Junior
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
#
# This file is part of l5x2c. To know more about it, acccess:
#    https://github.com/alairjunior/l5x2c
#
################################################################################
import sys
import argparse
import traceback
from runglex import runglex
from rungyacc import rungyacc
from l5xparser import parse_l5x

####################################################
#
# ADD THE HEADER TO THE C FILE
#
###################################################
def addHeader(f):
    f.write("/* This file was generated automatically by l5x2c */\n")
    f.write("/*     https://github.com/alairjunior/l5x2c       */\n")
    f.write("#include <assert.h>\n\n")

####################################################
#
# ADD STACK HANDLING FUNCTIONS AND VARIABLES
#
###################################################
def addStackFunctions(f):
    f.write('''
int stack[100] = {0};
int top = 0;
int acc() {return stack[top-1];}
void push(int x) {stack[top++]=x;}
int pop() {return stack[--top];}
void and() {int a = pop(); int b = pop(); push(a && b);}
void or() {int a = pop(); int b = pop(); push(a || b);}
void clear(){top=0;}
\n\n''')
    

####################################################
#
# PROCESSES THE RUNGS
#
###################################################
def processRungs(f, routine):
    # build the lexer
    lexer = runglex()
    # Build the parser
    parser = rungyacc()
    for rung in routine:
        f.write("    //%s\n" % (rung))
        try:
            f.write("    %s\n" % (parser.parse(rung)))
        except SyntaxError as e:
            f.write("    Syntax Error")
        finally:
            f.write("\n\n")
####################################################
#
# ADDS ROUTINE FUNCTION TO THE C FILE
#
###################################################
def addFunction(f, program, routine, rungs):
    f.write("/* Function for Routine %s of program %s */\n" % (routine,program))
    f.write("void %s_%s() {\n" % (program,routine))
    processRungs(f,rungs)
    f.write("}\n\n")


####################################################
#
# TRANSLATES THE DICTIONARY TO A C FILE
#
###################################################
def dict2c(l5x, output):
    with open(output, 'w') as f:
        addHeader(f)
        addStackFunctions(f)
        programs = l5x['programs']
        for program in programs:
            routines = programs[program]['routines']
            for routine in routines:
                addFunction(f, program, routine, routines[routine]['rungs'])
        

####################################################
#
# MAIN SCRIPT FOR COMMAND LINE EXECUTION
#
###################################################
def main():
    description = "Converts a Rockwell's L5X file into a C program"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("input")
    parser.add_argument("output")
    
    args = vars(parser.parse_args())
    try:
        l5x_data = parse_l5x(args['input'])
        dict2c(l5x_data, args['output'])
    except Exception as e:
        print(e.message)
  
if __name__== "__main__":
    main()
