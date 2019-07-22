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
        p[0] = 'clear();push(1);' + p[1] + p[2]
        
    def p_rung_o(p):
        'rung : output_list SEMICOLON'
        p[0] = 'clear();push(1);' + p[1]

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
        p[0] = p[1]
        
    def p_input_list_ii(p):
        'input_list : input_list input_instruction'
        p[0] = p[1] + p[2]

    def p_input_list_b(p):
        'input_list : input_branch'
        p[0] = p[1]

    def p_input_list_ib(p):
        'input_list : input_list input_branch'
        p[0] = p[1] + p[2]

    ################################################################################
    #
    #   INPUT_BRANCH    :      [ INPUT_LEVEL ]
    #                           | []
    #
    ################################################################################
    def p_input_branch_l(p):
        'input_branch : LBRA input_level RBRA'
        p[0] = 'push(acc());' + p[2] + 'or();'

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
        p[0] = p[1] + 'or();push(acc());' + p[3]

    def p_input_level_i(p):
        'input_level : input_list'
        p[0] = p[1]
        
    def p_input_level_c(p):
        'input_level : COMMA'
        p[0] = 'push(acc());or();push(acc());'
        
        
    def p_input_level_l(p):
        'input_level : COMMA input_level'
        p[0] = 'push(acc());or();push(acc());' + p[2]
        
    ################################################################################
    #
    #   OUTPUT_LIST     :      OUTPUT_INSTRUCTION
    #                           | OUTPUT_BRANCH
    #
    ################################################################################
    def p_output_list_i(p):
        'output_list : output_instruction'
        p[0] = p[1]
        
    def p_output_list_b(p):
        'output_list : output_branch'
        p[0] = p[1]
        
    ################################################################################
    #
    #   OUTPUT_BRANCH   :      [ OUTPUT_LEVEL ]
    #
    ################################################################################
    def p_output_branch_l(p):
        'output_branch : LBRA output_level RBRA'
        p[0] = 'push(acc());' + p[2] + 'or();'

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
        p[0] = p[1] + p[2] + 'or();push(acc());' + p[4]

    def p_output_level_ol(p):
        'output_level : output_list COMMA output_level'
        p[0] = p[1] + 'or();push(acc());' + p[3]

    def p_output_level_io(p):
        'output_level : input_list output_list'
        p[0] = p[1] + p[2]
        
    def p_output_level_o(p):
        'output_level : output_list'
        p[0] = p[1]
        
    ################################################################################
    #
    #   INPUT INSTRUCTIONS
    #
    ################################################################################
    def p_input_instruction_xic(p):
        'input_instruction : XIC LPAR TAG RPAR'
        p[0] = 'push(' + p[3] + ');and();'
        
    def p_input_instruction_xio(p):
        'input_instruction : XIO LPAR TAG RPAR'
        p[0] = 'push(!' + p[3] + ');and();'
    
    def p_input_instruction_ons(p):
        'input_instruction : ONS LPAR TAG RPAR'
        p[0] = 'if(' + p[3] + '==acc()){if(acc()){pop();push(0);}}else{' + p[3] + '=acc();}'
        
    ################################################################################
    #
    #   OUTPUT INSTRUCTIONS
    #
    ################################################################################
    def p_output_instruction_ote(p):
        'output_instruction : OTE LPAR TAG RPAR'
        p[0] = p[3] + '=acc();pop();push(0);'
        
    def p_output_instruction_otu(p):
        'output_instruction : OTU LPAR TAG RPAR'
        p[0] = 'if(acc())' + p[3] + '=0;pop();push(0);'
        
    def p_output_instruction_otl(p):
        'output_instruction : OTL LPAR TAG RPAR'
        p[0] = 'if(acc())' + p[3] + '=1;pop();push(0);'
    
    def p_output_instruction_res(p):
        'output_instruction : RES LPAR TAG RPAR'
        p[0] = 'if(acc())' + p[3] + '=0;pop();push(0);'
        
    def p_output_instruction_mov(p):
        'output_instruction : MOV LPAR TAG COMMA TAG RPAR'
        p[0] = 'if(acc())' + p[5] + '=' + p[3] + ';pop();push(0);'
        
    def p_output_instruction_mov(p):
        'output_instruction : TON LPAR TAG COMMA UNDEF_VAL COMMA UNDEF_VAL RPAR'
        p[0] = 'ton(acc(),' + p[3] + ');pop();push(0);'
        
    ################################################################################
    #
    #   ERROR RULE
    #
    ################################################################################
    def p_error(p):
        print("Syntax error at '%s'" % repr(p))
        raise SyntaxError
        
        
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
    
    #data = "XIO(A)[XIC(B) XIC(C) ,XIC(D) ]XIO(E)OTE(F);"
    data = "XIO(A)[XIC(B) XIC(C) ,XIC(D) ]XIO(E)[[XIC(F),XIC(G)]OTE(H),XIC(I)OTE(J)];"
    #data = "XIO(Timer_Rst_Comandos.DN)[XIC(Q3K26D1.TAB) XIC(Q3K26D1.CON) ,XIC(Q3K26D1.CAB) ]XIO(Q3K26D1.LAB)OTE(Q3K26D1.CAB);"
    #data = "XIO(Timer_Rst_Comandos.DN)[XIC(Q3K26D1.TAB) XIC(Q3K26D1.CON) ,XIC(Q3K26D1.CAB) ]XIO(Q3K26D1.LAB)[[XIC(C),XIC(D)]OTE(Q3K26D1.CAB),XIC(A)OTE(B)];"
    #data = "XIO(C)XIC(B)OTE(A);"
    
    #data = "[OTE(H),OTE(J)];"
    
    print(data)
    # Give the parser some input
    result = parser.parse(data)
    print(result)
    
if __name__== "__main__":
    main()
