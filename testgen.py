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
import logging
import argparse
from string import Template
from runglex import tokens
from runglex import runglex
from rungyacc import rungyacc

test_cases = [
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
    {
        "rung" : "XIC(a)[XIC(b)XIO(c),XIO(b)XIC(c)]XIC(d)OTE(e)OTE(f);",
        "template" : 
'''
    bool a,b,c,d,e,f;
    a = nondet_bool();
    b = nondet_bool();
    c = nondet_bool();
    d = nondet_bool();
    $rung
    assert(e == (a && (b && !c || !b && c) && d));
    assert(f == (a && (b && !c || !b && c) && d));

'''
    },
    {
        "rung" : "XIC(a)[XIC(b)XIO(c),XIO(b)XIC(c)][XIC(d)OTE(e),XIO(d)OTE(f)]OTE(g);",
        "template" : 
'''
    // Rung:
    // XIC(a)[XIC(b)XIO(c),XIO(b)XIC(c)][XIC(d)OTE(e),XIO(d)OTE(f)]OTE(g);
    // is invalid and should not be generated. Rung parser is wrong!
    assert(false);
'''
    },
    {
        "rung" : "XIC(a)MOV(b,c)MOV(b,d);",
        "template" : 
'''
    bool a = nondet_bool();
    int b = nondet_int();
    int c = nondet_int();
    int d = nondet_int();
    int old_c = c;
    int old_d = d;
    $rung
    if (a) assert(b == c);
    if (a) assert(b == d);
    if (!a) assert (c == old_c);
    if (!a) assert (d == old_d);
    
'''
    },
    {
        "rung" : "XIC(a)TON(t,?,?);",
        "template" : 
'''
    bool a;
    bool reset = false;
    int count = 0;
    int iterations = 30;
    
    timer t = {
        .EN = nondet_bool(),
        .TT = nondet_bool(),
        .DN = nondet_bool(),
        .PRE = nondet_int(),
        .ACC = nondet_int()
    };
    
    assume(t.ACC >= 0);
    assume(t.PRE < (iterations - 1) * get_scan_time());
    assume(t.PRE > 0);
    
    for (int i = 0; i < iterations; ++i) {
        a = nondet_bool();
        
        $rung
        
        if (!a) reset = true;
        
        if (a) ++count;
        else count=0;
        
        if (reset) {
            if (count > ceil((double)t.PRE / (double)get_scan_time()))
                assert(t.DN);
            else
                assert(!t.DN);
        }
        
        assert(a == t.EN);   
        
        assert(t.TT == (t.EN && !t.DN));
    }
    
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
        f.write('int nondet_int(){ int x; return x; }\n')
        f.write('bool nondet_bool(){ bool x; return x; }\n\n')
        f.write('void assume (bool e) { while (!e) ; }\n\n')

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
    
    # supress syntax error messages
    logger = logging.getLogger('l5x2c')
    logger.setLevel(logging.CRITICAL)
    
    # build the lexer
    lexer = runglex()
    # Build the parser
    rungparser = rungyacc()
    
    if not os.path.exists('tests'):
        os.makedirs('tests')
    
    with open('tests/tests.c', 'w') as f:
        addTemplates(f,parameters)
        tests = []
        for i in range(0,len(test_cases)):
            try:
                rung = rungparser.parse(test_cases[i]['rung'])
                f.write('void test_%d() {\n' % (i+1))
                template = Template(test_cases[i]['template'])
                f.write(template.substitute({'rung': rung}))            
                f.write('}\n\n')
                tests.append(i)
            except SyntaxError:
                pass
        
        f.write('int main() {\n')
        for test in tests:
            f.write('    test_%d();\n' % (test+1))
        f.write('}\n')
    
if __name__== "__main__":
    main()
