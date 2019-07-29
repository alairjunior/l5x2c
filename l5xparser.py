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

class l5xparser():
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
    def parse_xml(self, filename):
        if filename == self.old_filename:
            return self.old_dom
        else:
            self.old_filename = filename
            self.old_dom = parse(filename)
            return self.old_dom


    ####################################################
    #
    # RETURNS THE LIST OF PROGRAMS IN THE L5X FILE
    #
    ###################################################
    def list_programs(self, args):
        dom = self.parse_xml(args['filename'])
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
    def list_routines(self, args):
        program_name = args['program']
        if (program_name is None):
            raise Exception("Define the working program to list the routines")
        
        dom = self.parse_xml(args['filename'])
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
    def list_rungs(self, args):
        program_name = args['program']
        if (program_name is None):
            raise Exception("Define the working program to list the rungs")
        
        routine_name = args['routine']
        if (routine_name is None):
            raise Exception("Define the working routine to list the rungs")
        
        dom = self.parse_xml(args['filename'])
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
    def build_value_member(self, member):
        return {
            'type': member.getAttribute('DataType'),
            'data': member.getAttribute('Value')
        }

    ####################################################
    #
    # PROCESS DATA STRUCTURE
    #
    ###################################################
    def process_data_structure(self, node, tagtype):
        entry = None
        for content in node.childNodes:
            if content.nodeType == content.ELEMENT_NODE:                            
                if content.getAttribute('DataType') == tagtype:
                    if content.tagName == 'Structure':
                        entry = {}
                        entry['type'] = 'struct'
                        entry['data'] = self.build_structure_member(content)
                    elif content.tagName == 'DataValue':
                        entry = {}
                        entry['type'] = 'value'
                        entry['data'] = self.build_value_member(content)
                    elif content.tagName == 'Array':
                        entry = {}
                        entry['type'] = 'array'
                        entry['data'] = self.build_array_member(content)
        return entry
        

    ####################################################
    #
    # BUILD AN ARRAY MEMBER
    #
    ###################################################
    def build_array_member(self, member):
        
        data = {}
        datatype = member.getAttribute('DataType')
        for element in member.getElementsByTagName('Element'):
            index = int(element.getAttribute('Index')[1:-1])
            if element.hasAttribute('Value'):
                data[index] = {
                    'type': 'value',
                    'data': {
                        'type': datatype,
                        'data': element.getAttribute('Value')
                    }
                }
            else:
                for structure in element.getElementsByTagName('Structure'):
                    if structure.getAttribute('DataType') == datatype:
                        data[index] = {
                            'type': 'struct',
                            'data': self.build_structure_member(structure)
                        }
        
        array = {
            'type': member.getAttribute('DataType'),
            'dimensions': member.getAttribute('Dimensions'),
            'data': data
        }
        
        return array

    ####################################################
    #
    # BUILD A STRUCTURE MEMBER
    #
    ###################################################
    def build_structure_member(self, member):
        
        data = {}
        for field in member.childNodes:
            if field.nodeType == field.ELEMENT_NODE:
                fieldname = field.getAttribute('Name')
                tagname = field.tagName
                if tagname == 'DataValueMember':
                    data[fieldname] = {
                        'type': 'value',
                        'data': self.build_value_member(field)
                    }
                elif tagname == 'ArrayMember':
                    data[fieldname] = {
                        'type': 'array',
                        'data': self.build_array_member(field)
                    }
                elif tagname == 'StructureMember':
                    data[fieldname] = {
                        'type': 'struct',
                        'data': self.build_structure_member(field)
                    }
                else:
                    logging.warning("Unsupported field type %s. Field %s was ignored" % (tagname,fieldname))
        
        
        structure = {
            'type': member.getAttribute('DataType'),
            'data': data
        }
        
        return structure


    ####################################################
    #
    # RETURN A DICT CONTAINING ALL TAGS
    #
    ###################################################
    def parse_l5x_tags(self, filename):
        dom = self.parse_xml(filename)
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
                loggin.warning("Unsupported parent tag: %s" % (parent_tag))
            
            for tag in tags.getElementsByTagName('Tag'):
                tagname = tag.getAttribute('Name')
                tagtype = tag.getAttribute('DataType')
                tagdata = None
                for data in tag.getElementsByTagName('Data'):
                    if data.hasAttribute('Format'):
                        if data.getAttribute('Format') == 'Decorated':
                            tagdata = data
                            break
                        
                if tagdata is None:
                    logging.warning("Tag %s has no Decorated Data. Ignored." % (tagname))
                    continue
                    
                result = self.process_data_structure(tagdata, tagtype)
                
                if result is None:
                    logging.warning("Unsupported tag type %s. Tag %s was ignored." % (tagtype, tagname))
                else:
                    entry[tagname] = result
                    
        return l5x_tags

    ####################################################
    #
    # RETURN A DICT CONTAINING ALL DATATYPES
    #
    ###################################################
    def parse_l5x_datatypes(self, filename):
        dom = self.parse_xml(filename)
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
    def parse(self, filename):
        l5x_data = {}
        args = {}
        args['filename'] = filename
        l5x_data['tags'] = self.parse_l5x_tags(filename)
        l5x_data['datatypes'] = self.parse_l5x_datatypes(filename)
        l5x_data['programs'] = {}
        for program_name in self.list_programs(args):
            args['program'] = program_name
            programs = l5x_data['programs']
            programs[program_name] = {}
            program = programs[program_name]
            program['routines'] = {}
            for routine_name in self.list_routines(args):
                args['routine'] = routine_name
                routines = program['routines']
                routines[routine_name] = {}
                routine = routines[routine_name]
                routine['rungs'] = self.list_rungs(args)
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
            l5xparser = l5xparser()
            print(l5xparser.parse(args['filename'])['tags'])
    except Exception as e:
        print(str(e))
        traceback.print_exc()
  
if __name__== "__main__":
    main()
