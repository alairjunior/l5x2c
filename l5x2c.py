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
from string import Template
from runglex import runglex
from rungyacc import rungyacc
from l5xparser import parse_l5x

####################################################
#
# ADD TEMPLATES TO THE GENERATED FILE
#
###################################################
def addTemplates(f, parameters):
    with open('plcmodel.template', 'r') as t:
        text = t.read()
        template = Template(text)
        f.write(template.substitute(parameters))
        

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
    f.write("\n/* Function for Routine %s of program %s */\n" % (routine,program))
    f.write("void %s_%s() {\n" % (program,routine))
    processRungs(f,rungs)
    f.write("}\n\n")


####################################################
#
# TRANSLATES THE DICTIONARY TO A C FILE
#
###################################################
def dict2c(l5x, output, parameters):
    with open(output, 'w') as f:
        addTemplates(f, parameters)
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
    parser.add_argument('-ss', '--stack_size', type=int, default=1000,
                            help="Stack size for the stack machine")
    parser.add_argument('-st', '--scan_time', type=int, default=100,
                            help="Scan time for the PLC model")
    
    args = vars(parser.parse_args())
    try:
        l5x_data = parse_l5x(args['input'])
        parameters = {
            'stack_size': args['stack_size'],
            'scan_time': args['scan_time']
        }
        dict2c(l5x_data, args['output'], parameters)
    except KeyError as e:
        print("Key Error: " + str(e))
  
if __name__== "__main__":
    main()
