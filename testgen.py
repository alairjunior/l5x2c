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
import os
import argparse
from string import Template
from runglex import tokens
from runglex import runglex
from rungyacc import rungyacc

tests = [
    {
        "rung" : "OTE(a);",
        "template" : 
'''
    bool a;
    $rung
    assert(a);

'''
    },
    {
        "rung" : "XIC(a)OTE(b);",
        "template" : 
'''
    bool a,b;
    a = nondet_bool();
    $rung
    assert(a == b);

'''
    },
    {
        "rung" : "XIC(a)[XIC(b)XIO(c),XIO(b)XIC(c)][XIC(d)OTE(e),XIO(d)OTE(f)];",
        "template" : 
'''
    bool a,b,c,d,e,f;
    a = nondet_bool();
    b = nondet_bool();
    c = nondet_bool();
    d = nondet_bool();
    $rung
    assert(e == (a && (b && !c || !b && c) && d));
    assert(f == (a && (b && !c || !b && c) && !d));

'''
    },
]

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
# MAIN SCRIPT FOR COMMAND LINE EXECUTION
#
###################################################
def main():
    description = "Generate tests for the runglex and rungyacc files"
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument('-ss', '--stack_size', type=int, default=1000,
                            help="Stack size for the stack machine")
    parser.add_argument('-st', '--scan_time', type=int, default=100,
                            help="Scan time for the PLC model")
    
    args = vars(parser.parse_args())
    
    parameters = {
        'stack_size': args['stack_size'],
        'scan_time': args['scan_time']
    }
    
    # build the lexer
    lexer = runglex()
    # Build the parser
    rungparser = rungyacc()
    
    if not os.path.exists('tests'):
        os.makedirs('tests')
    
    with open('tests/tests.c', 'w') as f:
        addTemplates(f,parameters)
        for i in range(0,len(tests)):
            f.write('void test_%d() {\n' % (i+1))
            rung = rungparser.parse(tests[i]['rung'])
            template = Template(tests[i]['template'])
            f.write(template.substitute({'rung': rung}))            
            f.write('}\n\n')
        
        f.write('int main() {\n')
        for i in range(0,len(tests)):
            f.write('    test_%d();\n' % (i+1))
        f.write('}\n')
    
if __name__== "__main__":
    main()
