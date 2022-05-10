#!/usr/bin/env python

#This script takes a leginon database of a single session and makes a folder linking to the micrographs/movies that haven't been hidded in the leginon UI

import mysql.connector
import argparse
import numpy as np
import os
import json



def main():
    
    with open("server_settings.json","r") as file:
        server_settings = json.load(file)

    db = mysql.connector.connect(**server_settings['db_info'])

    parser = argparse.ArgumentParser()

    parser.add_argument('session')

    parser.add_argument('output', default = None)

    parser.add_argument('--ext',default='tif')

    parser.add_argument('--stain',action='store_true',default=False)

    results = parser.parse_args()

    session = results.session

    output = results.output

    ext = results.ext

    stain = results.stain

    cursor = db.cursor()

    if stain:
        ext = '.mrc'
        query = 'SELECT AcquisitionImageData.`filename`, ViewerImageStatus.`status`,SessionData.`image path` FROM AcquisitionImageData INNER JOIN SessionData ON AcquisitionImageData.`REF|SessionData|session` = SessionData.`DEF_id` LEFT JOIN ViewerImageStatus ON AcquisitionImageData.`DEF_id` = ViewerImageStatus.`REF|AcquisitionImageData|image` WHERE AcquisitionImageData.`filename` LIKE \'%en\' AND SessionData.`name` = \'' + session + '\''
    else:
        ext = '.frames.' + ext
        query = 'SELECT AcquisitionImageData.`filename`, ViewerImageStatus.`status`,SessionData.`frame path` FROM AcquisitionImageData INNER JOIN SessionData ON AcquisitionImageData.`REF|SessionData|session` = SessionData.`DEF_id` LEFT JOIN ViewerImageStatus ON AcquisitionImageData.`DEF_id` = ViewerImageStatus.`REF|AcquisitionImageData|image` WHERE AcquisitionImageData.`filename` LIKE \'%en\' AND SessionData.`name` = \'' + session + '\''

    cursor.execute(query)

    data = cursor.fetchall()

    if not output.endswith('/'):
        output = output + '/'

    if not os.path.exists(output):
        os.mkdir(output)

    for image in data:
        image_name = image[0] + ext
        if image[1] != 'hidden' and image[1] != 'trash':
            os.symlink(image[2] + '/' + image_name, output + image_name)



    cursor.close()

    db.close()

if __name__ == "__main__":
    main()
