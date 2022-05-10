#!/usr/bin/env python


#This script takes an input Relion .star file of averages and creates a grid of images of the averages
#Some averages can be highlighted in red by inputing a list


import numpy as np
import argparse
from EMAN2 import EMData
from EMAN2 import EMNumPy
from PIL import Image


def parse_star3(file_in):

    header_dict = {}
    value_dict = {}
    data = 'data_'

    with open(file_in,'r') as fi:

        for ln in fi:

            if ln.startswith('data_'):
                data = ln.split()[0]
                if not data in header_dict:
                    header_dict[data] = []
                if not data in value_dict:
                    value_dict[data] = []

            elif ln.startswith('_'):
                header_ln = ln.split()
                header = header_ln[0].strip()[1:]
                header_dict[data].append(header)

                if len(header_ln) == 2:
                    header_val = header_ln[1].strip()
                    if not header_val.startswith('#'):
                        value_dict[data].append({header:header_val})

            elif not ln.startswith('loop_') and ln.strip() and not ln.startswith('#'):
                values = [x.strip() for x in ln.split()]
                value_dict[data].append(dict(zip(header_dict[data],values)))

    return value_dict, header_dict

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument('star_in')
    parser.add_argument('png_out')
    parser.add_argument('-n','--averages',type=int,nargs='+',default=None) #List of images to plot, default is all, index starts at 1 (relion convention)
    parser.add_argument('-l','--highlight',type=int,nargs='+',default=[]) #List of images to highlight, default is none
    parser.add_argument('-c','--columns',type=int,default=None) #Number of columns
    parser.add_argument('-s','--sort',action='store_true',default=False) #Sort images
    parser.add_argument('--sort_name',default='rlnClassDistribution') #Value for which to sort, default is rlnClassDistribution
    parser.add_argument('--relion_dir',default='')
    parser.add_argument('--margin',type=float,default=0.04)
    parser.add_argument('--dmargin',type=float,default=0.0)
    parser.add_argument('--pad',type=int,default=-1)
    parser.add_argument('--dpad',type=int,default=0)
    parser.add_argument('--ignore',action='store_true',default=False)

    arguments = parser.parse_args()

    star_in = arguments.star_in
    png_out = arguments.png_out
    n = arguments.averages
    sort_name = arguments.sort_name
    relion_dir = arguments.relion_dir
    sort = arguments.sort
    columns = arguments.columns
    highlight = arguments.highlight
    margin = arguments.margin
    dmargin = arguments.dmargin
    pad = arguments.pad
    dpad = arguments.dpad
    ignore = arguments.ignore




    data_tot, headers = parse_star3(star_in)
    data = data_tot['data_model_classes']

    mrcs = relion_dir + data[0]['rlnReferenceImage'].split('@')[1]

    if n:
        num = len(n)
    else:
        num = len(data)
        n = list(range(1,num+1))

    img_list = []

    for i in n:
        a = EMData()
        a.read_image(mrcs,i - 1)
        img_data = a.get_data_as_vector()
        if ignore:
            if max(img_data) - min(img_data) > 0:
                img_list.append({'img':a,'num':i,'sort':data[i-1][sort_name]})
            else:
                num = num - 1
        else:
            img_list.append({'img':a,'num':i,'sort':data[i-1][sort_name]})

    if sort:
        img_list = sorted(img_list, key = lambda i: i['sort'],reverse=True)

    if not columns:
        columns = int(np.ceil(np.sqrt(num)))
    rows = int(np.ceil(float(num)/float(columns)))

    imgsize = img_list[0]['img'].get_xsize()
    if pad < 0:
        pad = int(margin*imgsize)
        dpad = int(dmargin*imgsize)
    dim = imgsize+ 2*pad + 2*dpad

    tot_arrayr = []
    tot_arrayg = []
    tot_arrayb = []

    for i in range(rows):
        temp_colr = []
        temp_colg = []
        temp_colb = []
        for j in range(columns):
            ind = columns*i + j
            if ind < num:
                img_np = EMNumPy.em2numpy(img_list[ind]['img'])
                if (np.max(img_np) - np.min(img_np)) != 0:
                    img_np = (img_np - np.min(img_np)) / (np.max(img_np) - np.min(img_np))
                if img_list[ind]['num'] in highlight:
                    imgr = np.pad(img_np,pad,'constant',constant_values=1)
                    imgg = np.pad(img_np,pad,'constant',constant_values=0)
                    imgb = np.pad(img_np,pad,'constant',constant_values=0)
                    if dpad > 0:
                        imgr = np.pad(imgr,dpad,'constant',constant_values=1)
                        imgg = np.pad(imgg,dpad,'constant',constant_values=1)
                        imgb = np.pad(imgb,dpad,'constant',constant_values=1)
                else:
                    imgr = np.pad(img_np,pad+dpad,'constant',constant_values=1)
                    imgg = np.pad(img_np,pad+dpad,'constant',constant_values=1)
                    imgb = np.pad(img_np,pad+dpad,'constant',constant_values=1)
            else:
                imgr = np.ones((dim,dim))
                imgg = np.ones((dim,dim))
                imgb = np.ones((dim,dim))

            temp_colr.append(np.uint8(imgr*255))
            temp_colg.append(np.uint8(imgg*255))
            temp_colb.append(np.uint8(imgb*255))

        tot_arrayr.append(temp_colr)
        tot_arrayg.append(temp_colg)
        tot_arrayb.append(temp_colb)



    img_totr = np.block(tot_arrayr)
    img_totg = np.block(tot_arrayg)
    img_totb = np.block(tot_arrayb)

    tot_array = np.dstack((img_totr,img_totg,img_totb))

    im = Image.fromarray(tot_array)

    im.save(png_out)
    

if __name__ == '__main__':
    main()




        















