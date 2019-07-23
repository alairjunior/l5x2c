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
import logging
import argparse
import traceback
from xml.dom.minidom import parse

####################################################
#
# CONSTRUCTS FOR THE 'LIST' OPTION
#
###################################################

constructs = ['tags', 'programs', 'routines', 'rungs']


####################################################
#
# PARSE XML FILE USING DOM
# obs: avoids parsing again if already parsed
###################################################
old_filename = None
old_dom = None
def parse_xml(filename):
    global old_filename
    global old_dom
    if filename == old_filename:
        return old_dom
    else:
        old_filename = filename
        old_dom = parse(filename)
        return old_dom


####################################################
#
# RETURNS THE LIST OF PROGRAMS IN THE L5X FILE
#
###################################################
def list_programs(args):
    dom = parse_xml(args['filename'])
    program_list = []
    for programs in dom.getElementsByTagName("Programs"):
        for program in programs.getElementsByTagName("Program"):
            program_list.append(program.getAttribute("Name"))
    
    return program_list




####################################################
#
# RETURNS THE LIST OF ROUTINES IN THE PROGRAM
#
###################################################
def list_routines(args):
    program_name = args['program']
    if (program_name is None):
        raise Exception("Define the working program to list the routines")
    
    dom = parse_xml(args['filename'])
    routine_list = []
    for programs in dom.getElementsByTagName("Programs"):
        for program in programs.getElementsByTagName("Program"):
            if (program.getAttribute("Name") == program_name):
                for routines in program.getElementsByTagName("Routines"):
                    for routine in routines.getElementsByTagName("Routine"):
                        routine_list.append(routine.getAttribute("Name"))
    
    return routine_list

####################################################
#
# RETURNS THE LIST OF RUNGS IN THE ROUTINE
#
###################################################
def list_rungs(args):
    program_name = args['program']
    if (program_name is None):
        raise Exception("Define the working program to list the rungs")
    
    routine_name = args['routine']
    if (routine_name is None):
        raise Exception("Define the working routine to list the rungs")
    
    dom = parse_xml(args['filename'])
    rung_list = []
    for programs in dom.getElementsByTagName("Programs"):
        for program in programs.getElementsByTagName("Program"):
            if (program.getAttribute("Name") == program_name):
                for routines in program.getElementsByTagName("Routines"):
                    for routine in routines.getElementsByTagName("Routine"):
                        if (routine.getAttribute("Name") == routine_name):
                            for rll in routine.getElementsByTagName("RLLContent"):
                                for rung in rll.getElementsByTagName("Rung"):
                                    for text in rung.getElementsByTagName("Text"):
                                        rung_list.append(text.firstChild.wholeText.strip())
    
    return rung_list

####################################################
#
# BUILD A VALUE MEMBER
#
###################################################
def build_value_member(member):
    return {
        'type': member.getAttribute('DataType'),
        'radix': member.getAttribute('Radix'),
        'value': member.getAttribute('Value')
    }

####################################################
#
# BUILD AN ARRAY MEMBER
#
###################################################
def build_array_member(member):
    
    values = []
    
    for value in member.getElementsByTagName('Element'):
        values.append({
            'index': value.getAttribute('Index')[1:-1],
            'value': value.getAttribute('Value'),
        })
    
    
    array = {
        'type': member.getAttribute('DataType'),
        'radix': member.getAttribute('Radix'),
        'dimensions': member.getAttribute('Dimensions'),
        'values': values
    }
    
    return array

####################################################
#
# BUILD A STRUCTURE MEMBER
#
###################################################
def build_structure_member(member):
    
    fields = {}
    for field in member.childNodes:
        if field.nodeType == field.ELEMENT_NODE:
            fieldname = field.getAttribute('Name')
            tagname = field.tagName
            if tagname == 'DataValueMember':
                fields[fieldname] = build_value_member(field)
            elif tagname == 'ArrayMember':
                fields[fieldname] = build_array_member(field)
            elif tagname == 'StructureMember':
                fields[fieldname] = build_structure_member(field)
            else:
                logging.warning("Unsupported field type %s. Field %s was ignored" % (tagname,fieldname))
    
    
    structure = {
        'type': member.getAttribute('DataType'),
        'fields': fields
    }
    
    return structure


####################################################
#
# RETURN A DICT CONTAINING ALL TAGS
#
###################################################
def parse_l5x_tags(filename):
    dom = parse_xml(filename)
    l5x_tags = {}
    for tags in dom.getElementsByTagName("Tags"):
        parent_tag = tags.parentNode.tagName
        entry = None
        if (parent_tag == 'Controller'):
            l5x_tags['Controller'] = {}
            entry = l5x_tags['Controller']
        elif (parent_tag == 'Program'):
            if not 'Programs' in l5x_tags:
                l5x_tags['Programs'] = {}
            l5x_tags['Programs'][tags.parentNode.getAttribute('Name')] = {}
            entry = l5x_tags['Programs'][tags.parentNode.getAttribute('Name')]
        else:
            raise Exception("Unsupported tag parent: %s" % (parent_tag))
        
        for tag in tags.getElementsByTagName('Tag'):
            decorated = False
            tagname = tag.getAttribute('Name')
            tagtype = tag.getAttribute('DataType')
            for data in tag.getElementsByTagName('Data'):
                if (data.getAttribute('Format') == 'Decorated'):
                    for details in data.childNodes:
                        if details.nodeType == details.ELEMENT_NODE:                            
                            if details.getAttribute('DataType') == tagtype:
                                if details.tagName == 'Structure':
                                    decorated = True
                                    entry[tagname] = {}
                                    entry[tagname]['type'] = details.tagName
                                    entry[tagname]['value'] = build_structure_member(details)
                                elif details.tagName == 'DataValue':
                                    decorated = True
                                    entry[tagname] = {}
                                    entry[tagname]['type'] = details.tagName
                                    entry[tagname]['value'] = build_value_member(details)
                                elif details.tagName == 'Array':
                                    decorated = True
                                    entry[tagname] = {}
                                    entry[tagname]['type'] = details.tagName
                                    entry[tagname]['value'] = build_array_member(details)
                
            if not decorated:
                logging.warning("Unsupported tag type %s. Tag %s was ignored" % (tagtype, tagname))
                
    return l5x_tags

####################################################
#
# RETURN A DICT CONTAINING ALL DATATYPES
#
###################################################
def parse_l5x_datatypes(filename):
    dom = parse_xml(filename)
    l5x_datatypes = {}
    for datatypes in dom.getElementsByTagName('DataTypes'):
        for datatype in datatypes.getElementsByTagName('DataType'):
            datatype_name = datatype.getAttribute('Name')
            l5x_datatypes[datatype_name] = {}
            for members in datatype.getElementsByTagName('Members'):
                l5x_datatypes[datatype_name]['members'] = {}
                members_dict = l5x_datatypes[datatype_name]['members']
                for member in members.getElementsByTagName('Member'):
                    members_dict[member.getAttribute('Name')] = {
                        'type': member.getAttribute('DataType'),
                        'dimension': member.getAttribute('Dimension'),
                        'radix': member.getAttribute('Radix'),
                    }
            
            for dependencies in datatype.getElementsByTagName('Dependencies'):
                l5x_datatypes[datatype_name]['dependencies'] = {}
                dependencies_dict = l5x_datatypes[datatype_name]['dependencies']
                for dependency in dependencies.getElementsByTagName('Dependency'):
                    dependencies_dict[dependency.getAttribute('Name')] = {
                        'type': dependency.getAttribute('Type'),
                    }
                    
    return l5x_datatypes

####################################################
#
# RETURNS A DICT CONTAINING ALL PROGRAMS
#
###################################################
def parse_l5x(filename):
    l5x_data = {}
    args = {}
    args['filename'] = filename
    l5x_data['tags'] = parse_l5x_tags(filename)
    l5x_data['datatypes'] = parse_l5x_datatypes(filename)
    l5x_data['programs'] = {}
    for program_name in list_programs(args):
        args['program'] = program_name
        programs = l5x_data['programs']
        programs[program_name] = {}
        program = programs[program_name]
        program['routines'] = {}
        for routine_name in list_routines(args):
            args['routine'] = routine_name
            routines = program['routines']
            routines[routine_name] = {}
            routine = routines[routine_name]
            routine['rungs'] = list_rungs(args)
    return l5x_data
    
####################################################
#
# MAIN SCRIPT FOR COMMAND LINE EXECUTION
#
###################################################
def main():
    description = "Parses the Rockwell's L5X file"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("filename")
    parser.add_argument('-p', '--program', help="define the working program")
    parser.add_argument('-r', '--routine', help="define the working program")
    parser.add_argument('-L', '--list', dest='construct',
                            help='print the selected program constructs',
                            choices=constructs)
  
    args = vars(parser.parse_args())
    try:
        if (args['construct']):
            print(globals()["list_"+args['construct']](args))
        else:
            print(parse_l5x(args['filename']))
    except Exception as e:
        print(str(e))
        traceback.print_exc()
  
if __name__== "__main__":
    main()
