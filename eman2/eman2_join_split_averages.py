#!/usr/bin/env python

#This script takes a series of EMAN2 mrc averages and joins them into a single average

import argparse
from EMAN2 import EMData

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_files',nargs='+')
    parser.add_argument('-o',dest='output')

    pin = parser.parse_args()

    input_files = pin.input_files

    output = pin.output

    n = len(input_files)

    input_stacks = [EMData.read_images(input_file) for input_file in input_files]


    input_stack_members = [[avg.get_attr('members') if type(avg.get_attr('members')) is list else [avg.get_attr('members')] for avg in stack] for stack in input_stacks]

    navg = len(input_stack_members[0])

    joined_members = []

    c = [input_stacks[0][i] for i in range(navg)]

    for i in range(navg):
        c[i] /= n
        c[i].set_attr('members',joined_members[i])
        c[i].write_image(output,i)
            
    
    


if __name__ == "__main__":
    main()

