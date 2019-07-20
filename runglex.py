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
}

tokens = [
   'LPAR',
   'RPAR',
   'LBRA',
   'RBRA',
   'COMMA',
   'SEMICOLON',
   'TAG',
] + list(reserved.values())



def runglex():
    # basic regular expressions for creating tokens
    VARIABLE  = r'([a-zA-Z_] ( [a-zA-Z0-9_] )* (\[ ([0-9])* \])?)'
    TAG       = r'(' + VARIABLE + '(\.' + VARIABLE + ')*)'

    # Regular expression rules for simple tokens
    t_LPAR      = r'\('
    t_RPAR      = r'\)'
    t_LBRA      = r'\['
    t_RBRA      = r'\]'
    t_COMMA     = r','
    t_SEMICOLON = r';'
    t_XIC       = r'XIC'
    t_XIO       = r'XIO'
    t_OTE       = r'OTE'
    t_OTU       = r'OTU'
    t_OTL       = r'OTL'
    t_TON       = r'TON'
    

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
    
    data = "XIO(Timer_Rst_Comandos.DN)[XIC(Q3K26D1.TAB) XIC(Q3K26D1.CON) ,XIC(Q3K26D1.CAB) ]XIO(Q3K26D1.LAB)OTE(Q3K26D1.CAB);"
    
    # Give the lexer some input
    lexer.input(data)

    # Tokenize
    while True:
        tok = lexer.token()
        if not tok: 
            break      # No more input
        print(tok)
  
if __name__== "__main__":
    main()
