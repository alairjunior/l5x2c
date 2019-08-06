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
import re
import sys
import logging
import argparse
import traceback
from string import Template
from runglex import runglex
from rungyacc import rungyacc
from l5xparser import l5xparser

####################################################
#
# LOOKUP TABLE FOR DATATYPE TRANSLATION
#
###################################################
datatype_translation_lut = {
    'SINT'   : 'int8_t',
    'INT'    : 'int16_t',
    'DINT'   : 'int32_t',
    'BOOL'   : 'bool',
    'BIT'    : 'bool',
    'REAL'   : 'float',
    'LINT'   : 'int64_t',
    'USINT'  : 'uint8_t',
    'UINT'   : 'unt16_t',
    'UDINT'  : 'unt32_t',
    'LREAL'  : 'double',
    'ULINT'  : 'uint64_t',
    'TIMER'  : 'timer',
    'COUNTER': 'counter'
}


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
# ADD A DATATYPE TO THE GENERATED FILE
#
###################################################
def addDataType(f, name, datatype):
    if name not in datatype_translation_lut:
        f.write('\n/* DataType %s  */\n' % (name))
        f.write('typedef struct %s_t {\n' % (name))
        for field in datatype['members']:
            typename = datatype['members'][field]['type']
            dimension = 0
            if 'dimension' in datatype['members'][field]:
                dimension = int(datatype['members'][field]['dimension'])
            
            inner_fields = datatype['members'][field]['fields']
            
            if len(inner_fields) > 0 :
                if dimension > 0:
                    logging.error("Cannot declare inner field for array. %s.%s" % (name,field))
                    raise Exception("Cannot declare inner field for array. %s.%s" % (name,field))
                
                field_type = datatype_translation_lut.get(typename, typename + '_t')
                f.write('\tunion {\n')
                f.write('\t\t%s %s;\n' % (field_type, field))
                f.write('\t\tstruct {\n')
                for inner in inner_fields:
                    bitfield = ': 1' if inner['type'] == 'BIT' else ''
                    field_type = datatype_translation_lut.get(inner['type'], inner['type'] + '_t')
                    f.write('\t\t\t%s %s%s;\n' % (field_type, inner['Name'], bitfield))
                f.write('\t\t};\n')
                f.write('\t};\n')
                
            else :
                bitfield = ': 1' if typename == 'BIT' else ''
                
                field_type = datatype_translation_lut.get(typename, typename + '_t')
                if dimension > 0:
                    f.write('\t%s %s[%d];\n' % (field_type, field, dimension))
                else:
                    f.write('\t%s %s%s;\n' % (field_type, field, bitfield))
                
                                
        f.write('} %s_t;\n' % (name))

####################################################
#
# ADD DATATYPES TO THE GENERATED FILE
#
###################################################
def addDataTypes(f, datatypes):
    
    f.write('\n/***************************************************\n')
    f.write('*                DataType Definitions              *\n')
    f.write('***************************************************/\n')
    
    unprocessed = list(datatypes.keys())
    while len(unprocessed) > 0:
        for name in unprocessed:
            datatype = datatypes[name]
            can_process = True
            if 'dependencies' in datatype:
                for dependency in datatype['dependencies']:
                    if dependency in unprocessed:
                        can_process = False
                        break
            if can_process:
                addDataType(f, name, datatype)
                unprocessed.remove(name)
                break

####################################################
#
# GET INITIAL VALUE STRING
#
###################################################
def get_initial_value(node):
    if node['type'] == 'value':
        return '=' + node['data']['data']
    elif node['type'] == 'array':
        result = " = { " 
        for index in node['data']['data']:
            ending = ', ' if int(index) != int(node['data']['dimensions']) - 1 else ''
            result += get_initial_value(node['data']['data'][index]).replace('=','',1) + ending
        return result + " }"
    elif node['type'] == 'struct':
        result = " = { "
        ending = '.'
        for field in node['data']['data']:
            result += (ending + field + get_initial_value(node['data']['data'][field]))
            ending = ', .'
        return result + ' }'
    else:
        logging.error("Undefined Tag major type: %s" %(node['type']))
        raise Exception("Undefined Tag major type: %s" %(node['type']))

####################################################
#
# ADD TAGS TO THE GENERATED FILE
#
###################################################
def addTags(f, tags):
    if len(tags) == 0: return
    
    f.write('\n/***************************************************\n')
    f.write('*                 Tags Definitions                 *\n')
    f.write('***************************************************/\n')
    
    for tag in tags:
        content = tags[tag]
        datatype = content['data']['type']
        if 'dimensions' in content['data']:
            dimensions = int(content['data']['dimensions'])
        else:
            dimensions = 0
        
        if dimensions > 0:
            dimensionstr = "[%d]" % dimensions
        else:
            dimensionstr = ''
            
        typename = datatype_translation_lut.get(datatype, datatype + '_t')
        f.write('%s %s%s%s;\n\n' % (typename, tag, dimensionstr, get_initial_value(content)))

####################################################
#
# PROCESS THE RUNGS
#
###################################################
def processRungs(f, routine):
    # build the lexer
    lexer = runglex()
    # Build the parser
    parser = rungyacc()
    for rung in routine:
        number = int(rung['number'])
        logic = rung['logic']
        
        if 'comment' in rung:
            comment = rung['comment']
            start = "<CBEFORE!"
            end = "!>"
            cbefore = re.search('%s(.*)%s' % (start, end), comment)
            start = "<CAFTER!"
            cafter = re.search('%s(.*)%s' % (start, end), comment)
        else:
            cbefore = None
            cafter = None
            
        f.write("    // (Rung %d) %s\n" % (number, logic))
        try:
            if cbefore is not None:
                f.write("    %s\n" % (cbefore.group(1).strip()))
            f.write("    %s\n" % (parser.parse(logic)))
            if cafter is not None:
                f.write("    %s\n" % (cafter.group(1).strip()))
        except SyntaxError as e:
            f.write("//    Syntax Error")
        finally:
            f.write("\n\n")

####################################################
#
# ADD ROUTINE FUNCTION TO THE C FILE
#
###################################################
def addFunction(f, program, routine, rungs):
    f.write("\n/* Function for Routine %s of program %s */\n" % (routine,program))
    f.write("void %s() {\n" % (routine))
    processRungs(f,rungs)
    f.write("}\n\n")


####################################################
#
# TRANSLATE THE DICTIONARY TO A C FILE
#
###################################################
def dict2c(l5x, output, parameters):
    with open(output, 'w') as f:
        addTemplates(f, parameters)
        addDataTypes(f, l5x['datatypes'])
        addTags(f, l5x['tags']['Controller'])
        f.write('\n/***************************************************\n')
        f.write('*               Program Definitions                *\n')
        f.write('***************************************************/\n')
        programs = l5x['programs']
        for program in programs:
            f.write("\n/* Program %s */\n" % (program))
            if 'Programs' in l5x['tags']:
                if program in l5x['tags']['Programs']:
                    addTags(f, l5x['tags']['Programs'][program])
            routines = programs[program]['routines']
            for routine in routines:
                addFunction(f, program, routine, routines[routine]['rungs'])
        

####################################################
#
# MAIN SCRIPT FOR COMMAND LINE EXECUTION
#
###################################################
def main():
    log = logging.getLogger('l5x2c')
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
        l5x = l5xparser()
        l5x_data = l5x.parse(args['input'])
        parameters = {
            'stack_size': args['stack_size'],
            'scan_time': args['scan_time']
        }
        dict2c(l5x_data, args['output'], parameters)
    except KeyError as e:
        log.critical("Key Error: " + str(e))
        traceback.print_exc()
        
if __name__== "__main__":
    main()
