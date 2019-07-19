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
################################################################################
import sys
import json
import argparse
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
    dom = parse_xml(args.file)
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
    program_name = args.program
    if (program_name is None):
        raise Exception("Define the working program to list the routines")
    
    dom = parse_xml(args.file)
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
    program_name = args.program
    if (program_name is None):
        raise Exception("Define the working program to list the rungs")
    
    routine_name = args.routine
    if (routine_name is None):
        raise Exception("Define the working routine to list the rungs")
    
    dom = parse_xml(args.file)
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
# MAIN SCRIPT
#
###################################################
def main():
    description = "Converts a Rockwell's L5X file into a C program"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("file")
    parser.add_argument('-p', '--program', help="define the working program")
    parser.add_argument('-r', '--routine', help="define the working program")
    parser.add_argument('-L', '--list', dest='construct',
                            help='print the selected program constructs',
                            choices=constructs)
  
    args = parser.parse_args()
    
    if (args.construct):
        try:
            print globals()["list_"+args.construct](args)
        except Exception as e:
            print e.message
    
  
if __name__== "__main__":
    main()
