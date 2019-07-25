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

from ply import lex
from ply.lex import TOKEN

# List of token names.
reserved = {
   'XIC' : 'XIC',
   'XIO' : 'XIO',
   'OTE' : 'OTE',
   'OTU' : 'OTU',
   'OTL' : 'OTL',
   'TON' : 'TON',
   'TOF' : 'TOF',
   'ONS' : 'ONS',
   'RES' : 'RES',
   'MOV' : 'MOV',
   'CTU' : 'CTU',
   'EQU' : 'EQU',
   'GEQ' : 'GEQ',
   'NEQ' : 'NEQ',
   'LEQ' : 'LEQ',
   'GRT' : 'GRT',
   'COP' : 'COP',
   'CPT' : 'CPT',
   'ADD' : 'ADD',
   'SUB' : 'SUB',
   'CLR' : 'CLR',
   'LIM' : 'LIM',
   'DIV' : 'DIV',
   'BTD' : 'BTD',
   'JSR' : 'JSR',
   'MSG' : 'MSG',
}

tokens = [
   'LPAR',
   'RPAR',
   'LBRA',
   'RBRA',
   'COMMA',
   'SEMICOLON',
   'TAG',
   'UNDEF_VAL',
   'COMM_TAG',
   'CPT_MINUS',
   'CPT_PLUS',
   'CPT_TIMES',
   'CPT_DIV',
   'NUMBER'
] + list(reserved.values())



def runglex():
    # basic regular expressions for creating tokens
    ID          = r'([a-zA-Z_] ( [a-zA-Z0-9_] )*)'
    OBJ_ID      = r'(' + ID + '(\.' + ID + ')*)'
    INDEX       = r'(\[ (([0-9])+ | (' + OBJ_ID + '))\])' 
    OBJ_INDEX   = r'(' + OBJ_ID + '(' + INDEX + ')?)'
    TAG         = r'(' + OBJ_INDEX + '(\.' + OBJ_INDEX + ')*(\.([0-9])+)?)'
    COMM_TAG    = r'(' + ID + ':([0-9])+:' + ID + '\.' + TAG + ')'

    # Regular expression rules for simple tokens
    t_LPAR      = r'\('
    t_RPAR      = r'\)'
    t_LBRA      = r'\['
    t_RBRA      = r'\]'
    t_COMMA     = r','
    t_SEMICOLON = r';'
    t_UNDEF_VAL = r'\?'
    t_XIC       = r'XIC'
    t_XIO       = r'XIO'
    t_OTE       = r'OTE'
    t_OTU       = r'OTU'
    t_OTL       = r'OTL'
    t_TON       = r'TON'
    t_TOF       = r'TOF'
    t_ONS       = r'ONS'
    t_RES       = r'RES'
    t_MOV       = r'MOV'
    t_CTU       = r'CTU'
    t_EQU       = r'EQU'
    t_GEQ       = r'GEQ'
    t_NEQ       = r'NEQ'
    t_LEQ       = r'LEQ'
    t_GRT       = r'GRT'
    t_COP       = r'COP'
    t_CPT       = r'CPT'
    t_ADD       = r'ADD'
    t_SUB       = r'SUB'
    t_CLR       = r'CLR'
    t_LIM       = r'LIM'
    t_DIV       = r'DIV'
    t_BTD       = r'BTD'
    t_JSR       = r'JSR'
    t_MSG       = r'MSG'
    t_CPT_MINUS = r'\-'
    t_CPT_PLUS  = r'\+'
    t_CPT_TIMES = r'\*'
    t_CPT_DIV   = r'/'
    t_NUMBER    = r'[0-9]*\.?[0-9]+([eE][\-\+]?[0-9]+)?'

    @TOKEN(COMM_TAG)
    def t_COMM_TAG(t):
        return t


    @TOKEN(TAG)
    def t_TAG(t):
        t.type = reserved.get(t.value,'TAG')  # Check for reserved words
        return t

    # A string containing ignored characters 
    t_ignore  = ' \t\n\r'


    # Define a rule so we can track line numbers
    def t_newline(t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    # Error handling rule
    def t_error(t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)
    
    return lex.lex()

####################################################
#
# MAIN SCRIPT FOR COMMAND LINE EXECUTION
#
###################################################
def main():
    # Build the lexer
    lexer = runglex()
    
    lexer.input(sys.stdin.readline())
    while True:
        tok = lexer.token()
        if not tok: 
            break
        print(tok)

  
if __name__== "__main__":
    main()
