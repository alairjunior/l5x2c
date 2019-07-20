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

################################################################################
#                          ---  RUNG GRAMMAR  ---
#
#
#   RUNG            :      INPUT_LIST OUTPUT_LIST ;
#                           | OUTPUT_LIST ;
#
#   INPUT_LIST      :      INPUT_INSTRUCTION
#                           | INPUT_LIST INPUT_INSTRUCTION
#                           | INPUT_BRANCH
#                           | INPUT_LIST INPUT_BRANCH
#
#   INPUT_BRANCH    :      [ INPUT_LEVEL ]
#                           | []
#
#   INPUT_LEVEL     :      INPUT_LIST , INPUT_LEVEL
#                           | INPUT_LIST
#                           | ,
#                           | , INPUT_LEVEL
#
#   OUTPUT_LIST     :      OUTPUT_INSTRUCTION
#                           | OUTPUT_BRANCH
#
#   OUTPUT_BRANCH   :      [ OUTPUT_LEVEL ]
#
#   OUTPUT_LEVEL    :      INPUT_LIST OUTPUT_LIST , OUTPUT_LEVEL
#                           | OUTPUT_LIST , OUTPUT_LEVEL
#                           | INPUT_LIST OUTPUT_LIST
#                           | OUTPUT_LIST
#
#   INPUT_INSTRUCTION list of instruction dependent rules
#
#   OUTPUT_INSTRUCTION list of instruction dependent rules
#
################################################################################

from ply import yacc
from runglex import tokens
from runglex import runglex


def rungyacc():
    ################################################################################
    #
    #   RUNG            :      INPUT_LIST OUTPUT_LIST
    #                           | OUTPUT_LIST
    #
    ################################################################################
    def p_rung_io(p):
        'rung : input_list output_list SEMICOLON'
        pass
        
    def p_rung_o(p):
        'rung : output_list SEMICOLON'
        pass

    ################################################################################
    #
    #   INPUT_LIST      :      INPUT_INSTRUCTION
    #                           | INPUT_LIST INPUT_INSTRUCTION
    #                           | INPUT_BRANCH
    #                           | INPUT_LIST INPUT_BRANCH
    #
    ################################################################################
    def p_input_list_i(p):
        'input_list : input_instruction'
        pass
        
    def p_input_list_ii(p):
        'input_list : input_list input_instruction'
        pass

    def p_input_list_b(p):
        'input_list : input_branch'
        pass

    def p_input_list_ib(p):
        'input_list : input_list input_branch'
        pass

    ################################################################################
    #
    #   INPUT_BRANCH    :      [ INPUT_LEVEL ]
    #                           | []
    #
    ################################################################################
    def p_input_branch_l(p):
        'input_branch : LBRA input_level RBRA'
        pass

    def p_input_branch_e(p):
        'input_branch : LBRA RBRA'
        pass

    ################################################################################
    #
    #   INPUT_LEVEL     :      INPUT_LIST , INPUT_LEVEL
    #                           | INPUT_LIST
    #                           | ,
    #                           | , INPUT_LEVEL
    #
    ################################################################################
    def p_input_level_il(p):
        'input_level : input_list COMMA input_level'
        pass

    def p_input_level_i(p):
        'input_level : input_list'
        pass
        
    def p_input_level_c(p):
        'input_level : COMMA'
        pass
        
    def p_input_level_l(p):
        'input_level : COMMA input_level'
        pass
        
    ################################################################################
    #
    #   OUTPUT_LIST     :      OUTPUT_INSTRUCTION
    #                           | OUTPUT_BRANCH
    #
    ################################################################################
    def p_output_list_i(p):
        'output_list : output_instruction'
        pass
        
    def p_output_list_b(p):
        'output_list : output_branch'
        pass
        
    ################################################################################
    #
    #   OUTPUT_BRANCH   :      [ OUTPUT_LEVEL ]
    #
    ################################################################################
    def p_output_branch_l(p):
        'output_branch : LBRA output_level RBRA'
        pass

    ################################################################################
    #
    #   OUTPUT_LEVEL    :      INPUT_LIST OUTPUT_LIST , OUTPUT_LEVEL
    #                           | OUTPUT_LIST , OUTPUT_LEVEL
    #                           | INPUT_LIST OUTPUT_LIST
    #                           | OUTPUT_LIST
    #
    ################################################################################
    def p_output_level_iol(p):
        'output_level : input_list output_list COMMA output_level'
        pass

    def p_output_level_ol(p):
        'output_level : output_list COMMA output_level'
        pass

    def p_output_level_io(p):
        'output_level : input_list output_list'
        pass
        
    def p_output_level_o(p):
        'output_level : output_list'
        pass
        
    ################################################################################
    #
    #   INPUT INSTRUCTIONS
    #
    ################################################################################
    def p_input_instruction_xic(p):
        'input_instruction : XIC LPAR TAG RPAR'
        pass
        
    def p_input_instruction_xio(p):
        'input_instruction : XIO LPAR TAG RPAR'
        pass
        
    ################################################################################
    #
    #   OUTPUT INSTRUCTIONS
    #
    ################################################################################
    def p_output_instruction_ote(p):
        'output_instruction : OTE LPAR TAG RPAR'
        pass
        
    ################################################################################
    #
    #   ERROR RULE
    #
    ################################################################################
    def p_error(p):
        print("Syntax error at '%s'" % repr(p))
        
        
    return yacc.yacc()

####################################################
#
# MAIN SCRIPT FOR COMMAND LINE EXECUTION
#
###################################################
def main():
    # build the lexer
    lexer = runglex()
    # Build the parser
    parser = rungyacc()
    
    data = "XIO(Timer_Rst_Comandos.DN)[XIC(Q3K26D1.TAB) XIC(Q3K26D1.CON) ,XIC(Q3K26D1.CAB) ]XIO(Q3K26D1.LAB)OTE(Q3K26D1.CAB);"
    
    # Give the parser some input
    result = parser.parse(data)
    print result
    
if __name__== "__main__":
    main()
