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
#   OUTPUT_LIST     :      OUTPUT_SEQ
#                           | OUTPUT_BRANCH
#
#   OUTPUT_SEQ      :      OUTPUT_INSTRUCTION
#                           | OUTPUT_SEQ OUTPUT_INSTRUCTION
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
#   !! OBS: OUTPUT_SEQ was added because Rockwell's ladder allows an output
#           instruction following another. Usually:
#               OUTPUT_LIST : OUTPUT_INSTRUCTION | OUTPUT_BRANCH
#
################################################################################
import sys
import logging
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
        p[0] = 'clear();push(true);' + p[1] + p[2]
        
    def p_rung_o(p):
        'rung : output_list SEMICOLON'
        p[0] = 'clear();push(true);' + p[1]

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
        p[0] = 'push(false);push(true);' + p[2] + 'or();and();'

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
        p[0] = p[1] + 'or();push(true);' + p[3]

    def p_input_level_i(p):
        'input_level : input_list'
        p[0] = p[1]
        
    def p_input_level_c(p):
        'input_level : COMMA'
        p[0] = 'or();push(true);'
        
        
    def p_input_level_l(p):
        'input_level : COMMA input_level'
        p[0] = 'or();push(true);' + p[2]
        
    ################################################################################
    #
    #   OUTPUT_LIST     :      OUTPUT_INSTRUCTION
    #                           | OUTPUT_BRANCH
    #
    ################################################################################
    def p_output_list_i(p):
        'output_list : output_seq'
        p[0] = p[1]
        
    def p_output_list_b(p):
        'output_list : output_branch'
        p[0] = p[1]
    
    ################################################################################
    #    
    #   OUTPUT_SEQ      :      OUTPUT_INSTRUCTION
    #                           | OUTPUT_SEQ OUTPUT_INSTRUCTION
    #
    ################################################################################
    def p_output_seq_i(p):
        'output_seq : output_instruction'
        p[0] = p[1]
        
    def p_output_seq_b(p):
        'output_seq : output_seq output_instruction'
        p[0] = p[1] + p[2]
    
    
    ################################################################################
    #
    #   OUTPUT_BRANCH   :      [ OUTPUT_LEVEL ]
    #
    ################################################################################
    def p_output_branch_l(p):
        'output_branch : LBRA output_level RBRA'
        p[0] = 'push(acc());' + p[2] + 'pop();'

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
        p[0] = p[1] + p[2] + 'pop();push(acc());' + p[4]

    def p_output_level_ol(p):
        'output_level : output_list COMMA output_level'
        p[0] = p[1] + 'pop();push(acc());' + p[3]

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
        'input_instruction : XIC LPAR parameter RPAR'
        p[0] = 'push(' + p[3] + ');and();'
        
    def p_input_instruction_xio(p):
        'input_instruction : XIO LPAR parameter RPAR'
        p[0] = 'push(!' + p[3] + ');and();'
    
    def p_input_instruction_ons(p):
        'input_instruction : ONS LPAR parameter RPAR'
        p[0] = 'if(' + p[3] + '==acc()){if(acc()){pop();push(false);}}else{' + p[3] + '=acc();}'
    
    def p_input_instruction_equ(p):
        'input_instruction : EQU LPAR parameter COMMA parameter RPAR'
        p[0] = 'push(%s==%s);and();' % (p[3],p[5])
    
    def p_input_instruction_geq(p):
        'input_instruction : GEQ LPAR parameter COMMA parameter RPAR'
        p[0] = 'push(%s>=%s);and();' % (p[3],p[5])
    
    def p_input_instruction_neq(p):
        'input_instruction : NEQ LPAR parameter COMMA parameter RPAR'
        p[0] = 'push(%s!=%s);and();' % (p[3],p[5])
        
    def p_input_instruction_leq(p):
        'input_instruction : LEQ LPAR parameter COMMA parameter RPAR'
        p[0] = 'push(%s<%s);and();' % (p[3],p[5])
        
    def p_input_instruction_grt(p):
        'input_instruction : GRT LPAR parameter COMMA parameter RPAR'
        p[0] = 'push(%s>%s);and();' % (p[3],p[5])

    def p_input_instruction_lim(p):
        'input_instruction : LIM LPAR parameter COMMA parameter COMMA parameter RPAR'
        p[0] = 'if(acc()){{if({low}<={high}){{if({low}>={value}||{value}>={high}){{pop();push(false);}}}}else{{if({low}<={value}||{value}<={high}){{pop();push(false);}}}}}}'.format(low=p[3], value=p[5], high=p[7])
    
        
    ################################################################################
    #
    #   OUTPUT INSTRUCTIONS
    #
    ################################################################################
    def p_output_instruction_ote(p):
        'output_instruction : OTE LPAR parameter RPAR'
        p[0] = p[3] + '=acc();'
        
    def p_output_instruction_otu(p):
        'output_instruction : OTU LPAR parameter RPAR'
        p[0] = 'if(acc())' + p[3] + '=0;'
        
    def p_output_instruction_otl(p):
        'output_instruction : OTL LPAR parameter RPAR'
        p[0] = 'if(acc())' + p[3] + '=1;'
    
    def p_output_instruction_res(p):
        'output_instruction : RES LPAR parameter RPAR'
        p[0] = 'if(acc())' + p[3] + '.ACC=0;'
        
    def p_output_instruction_mov(p):
        'output_instruction : MOV LPAR parameter COMMA parameter RPAR'
        p[0] = 'if(acc())' + p[5] + '=' + p[3] + ';'
    
    def p_output_instruction_cop(p):
        'output_instruction : COP LPAR parameter COMMA parameter COMMA parameter RPAR'
        logging.warning("Instruction COP is not supported. Instruction was ignored.")
        p[0] = ''  
    
    def p_output_instruction_ton(p):
        'output_instruction : TON LPAR parameter COMMA UNDEF_VAL COMMA UNDEF_VAL RPAR'
        p[0] = 'ton(acc(), &' + p[3] + ');'
    
    def p_output_instruction_tof(p):
        'output_instruction : TOF LPAR parameter COMMA UNDEF_VAL COMMA UNDEF_VAL RPAR'
        p[0] = 'tof(acc(), &' + p[3] + ');'
        
    def p_output_instruction_ctu(p):
        'output_instruction : CTU LPAR parameter COMMA UNDEF_VAL COMMA UNDEF_VAL RPAR'
        p[0] = 'ctu(acc(), &' + p[3] + ');'
        
    def p_output_instruction_jsr(p):
        'output_instruction : JSR LPAR parameter COMMA NUMBER RPAR'
        p[0] = 'if(acc())%s();' % (p[3])
        
    def p_output_instruction_btd(p):
        'output_instruction : BTD LPAR parameter COMMA NUMBER COMMA parameter COMMA NUMBER COMMA NUMBER RPAR'
        logging.warning("Instruction BTD is not supported. Instruction was ignored.")
        p[0] = ''
        
    def p_output_instruction_add(p):
        'output_instruction : ADD LPAR parameter COMMA parameter COMMA parameter RPAR'
        p[0] = 'if(acc()){%s=%s+%s;};' % (p[7],p[3],p[5])
        
    def p_output_instruction_sub(p):
        'output_instruction : SUB LPAR parameter COMMA parameter COMMA parameter RPAR'
        p[0] = 'if(acc()){%s=%s-%s;};' % (p[7],p[3],p[5])
    
    def p_output_instruction_clr(p):
        'output_instruction : CLR LPAR parameter RPAR'
        p[0] = 'if(acc()){%s=0;};' % (p[3])
    
    def p_output_instruction_div(p):
        'output_instruction : DIV LPAR parameter COMMA parameter COMMA parameter RPAR'
        p[0] = 'if(acc()){%s=%s/%s;};' % (p[7],p[3],p[5])
        
    def p_output_instruction_cpt(p):
        'output_instruction : CPT LPAR parameter COMMA cpt_expression RPAR'
        p[0] = 'if(acc()){%s=%s;};' % (p[3],p[5])
        
    def p_output_instruction_msg(p):
        'output_instruction : MSG LPAR parameter RPAR'
        logging.warning("Instruction MSG is not supported. Instruction was ignored.")
        p[0] = ''
        
    ################################################################################
    #
    #   PARAMETERS
    #
    ################################################################################
    def p_parameter_tag(p):
        'parameter : TAG'
        p[0] = p[1]
    
    def p_parameter_comm_tag(p):
        'parameter : COMM_TAG'
        p[0] = p[1]
        
    def p_parameter_number(p):
        'parameter : NUMBER'
        p[0] = p[1]
        
    def p_parameter_neg_number(p):
        'parameter : CPT_MINUS NUMBER'
        p[0] = p[1]
        
    ################################################################################
    #
    #   CPT EXPRESSION
    #       
    #   expression : expression PLUS expression
    #       | expression MINUS expression
    #       | expression TIMES expression
    #       | expression DIVIDE expression
    #       | LPAREN expression RPAREN
    #       | NUMBER
    #       | parameter
    #
    ################################################################################
    precedence = (
        ('left', 'CPT_PLUS', 'CPT_MINUS'),
        ('left', 'CPT_TIMES', 'CPT_DIV'),
    )
    def p_cpt_expression_plus(p):
        'cpt_expression : cpt_expression CPT_PLUS cpt_expression'
        p[0] = '%s+%s' % (p[1],p[3])
        
    def p_cpt_expression_minus(p):
        'cpt_expression : cpt_expression CPT_MINUS cpt_expression'
        p[0] = '%s-%s' % (p[1],p[3])
        
    def p_cpt_expression_times(p):
        'cpt_expression : cpt_expression CPT_TIMES cpt_expression'
        p[0] = '%s*%s' % (p[1],p[3])
        
    def p_cpt_expression_div(p):
        'cpt_expression : cpt_expression CPT_DIV cpt_expression'
        p[0] = '%s/%s' % (p[1],p[3])
        
    def p_cpt_expression_par(p):
        'cpt_expression : LPAR cpt_expression RPAR'
        p[0] = '(%s)' % (p[2])
    
    def p_cpt_expression_number(p):
        'cpt_expression : NUMBER'
        p[0] = p[1]
    
    def p_cpt_expression_parameter(p):
        'cpt_expression : parameter'
        p[0] = p[1]
    
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
    
    result = parser.parse(sys.stdin.readline())
    print(result)
    
if __name__== "__main__":
    main()
