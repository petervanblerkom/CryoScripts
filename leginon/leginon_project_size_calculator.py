#!/usr/bin/env python

import mysql.connector
import os
import sys
import numpy as np
import argparse

def get_size(start_path = '.'):
    total_size = 0
    if not os.path.islink(start_path):
        for dirpath, dirnames, filenames in os.walk(start_path):
            if not os.path.islink(dirpath):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if not os.path.islink(fp):
                        total_size += os.path.getsize(fp)

    return total_size

def bytes_to_string(size):
    if size > 0:
        si_mag = int(np.log(size)/np.log(1000))
    else:
        si_mag = 0
    num = float(size) / (1000.0 ** si_mag)
    if si_mag >= 4:
        outstring = '{:05.1f} TB'.format(num)
    elif si_mag == 3:
        outstring = '{:05.1f} GB'.format(num)
    elif si_mag ==2:
        outstring = '{:05.1f} MB'.format(num)
    elif si_mag ==1:
        outstring = '{:05.1f} KB'.format(num)
    else:
        outstring = '{:03.0f}   B'.format(num)
    return outstring

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument('output')

    parser.add_argument('-a','--show_all',action='store_true',default=False)

    inputs = parser.parse_args()

    output = inputs.output

    show_all = inputs.show_all


    db = mysql.connector.connect(
      host="amc-cobolt",
      user="leginon_access",
      passwd="cryoem5978"
    )

    cursor = db.cursor()

    query = 'SELECT projectdb.projects.name, leginondb.SessionData.name FROM leginondb.SessionData INNER JOIN projectdb.projectexperiments ON leginondb.SessionData.DEF_id = projectdb.projectexperiments.`REF|leginondata|SessionData|session` INNER JOIN projectdb.projects ON projectdb.projectexperiments.`REF|projects|project` = projectdb.projects.DEF_id'

    cursor.execute(query)

    data = cursor.fetchall()

    cursor.close()

    db.close()

    project_dict = {}

    for session in data:
        session_name = session[1]
        project_name = session[0]

        frames2 = '/cryostor2/frames/' + session_name
        appion2 = '/cryostor2/appion/' + session_name
        leginon2 = '/cryostor2/leginon/' + session_name

        frames3 = '/cryostor3/frames/' + session_name
        appion3 = '/cryostor3/appion/' + session_name
        leginon3 = '/cryostor3/leginon/' + session_name

        frames1 = '/cryostor1/archive/' + session_name + '/frames/' + session_name
        appion1 = '/cryostor1/archive/' + session_name + '/appion/' + session_name
        leginon1 = '/cryostor1/archive/' + session_name + '/leginon/' + session_name

        frames_size1 = get_size(frames1)
        appion_size1 = get_size(appion1)
        leginon_size1 = get_size(leginon1)
        combined_size1 = frames_size1 + appion_size1 + leginon_size1

        frames_size2 = get_size(frames2)
        appion_size2 = get_size(appion2)
        leginon_size2 = get_size(leginon2)
        combined_size2 = frames_size2 + appion_size2 + leginon_size2

        frames_size3 = get_size(frames3)
        appion_size3 = get_size(appion3)
        leginon_size3 = get_size(leginon3)
        combined_size3 = frames_size3 + appion_size3 + leginon_size3


        if project_name not in project_dict:
            project_dict[project_name] = {'sessions':[],'frames':[],'appion':[],'leginon':[],'combined':[],'tot_frames_size':[0,0,0],'tot_appion_size':[0,0,0],'tot_leginon_size':[0,0,0],'tot_size':[0,0,0],'complete_size':0}

        project_dict[project_name]['sessions'].append(session_name)
        project_dict[project_name]['frames'].append([frames_size1,frames_size2,frames_size3])
        project_dict[project_name]['appion'].append([appion_size1,appion_size2,appion_size3])
        project_dict[project_name]['leginon'].append([leginon_size1,leginon_size2,leginon_size3])
        project_dict[project_name]['combined'].append([combined_size1,combined_size2,combined_size3])
        project_dict[project_name]['tot_frames_size'] = [a + b for a, b in zip(project_dict[project_name]['tot_frames_size'],[frames_size1,frames_size2,frames_size3])]
        project_dict[project_name]['tot_appion_size'] = [a + b for a, b in zip(project_dict[project_name]['tot_appion_size'],[appion_size1,appion_size2,appion_size3])]
        project_dict[project_name]['tot_leginon_size'] = [a + b for a, b in zip(project_dict[project_name]['tot_leginon_size'],[leginon_size1,leginon_size2,leginon_size3])]
        project_dict[project_name]['tot_size'] = [a + b for a, b in zip(project_dict[project_name]['tot_size'],[combined_size1,combined_size2,combined_size3])]
        project_dict[project_name]['complete_size'] = sum(project_dict[project_name]['tot_size'])


    with open(output,'w') as fout:
        for project in project_dict:
            temp_dict = project_dict[project]
            fout.write('Project: ' + project + '\n')
            fout.write('    Total Size on Disks         :  {}\n'.format(bytes_to_string(temp_dict['complete_size'])))
            fout.write('      Total Size on cryostor1   :    {}\n'.format(bytes_to_string(temp_dict['tot_size'][0])))
            fout.write('        /cryostor1/../leginon/  :      {}\n'.format(bytes_to_string(temp_dict['tot_leginon_size'][0])))
            fout.write('        /cryostor1/../appion/   :      {}\n'.format(bytes_to_string(temp_dict['tot_appion_size'][0])))
            fout.write('        /cryostor1/../frames/   :      {}\n'.format(bytes_to_string(temp_dict['tot_frames_size'][0])))
            fout.write('      Total Size on cryostor2   :    {}\n'.format(bytes_to_string(temp_dict['tot_size'][1])))
            fout.write('        /cryostor2/leginon/     :      {}\n'.format(bytes_to_string(temp_dict['tot_leginon_size'][1])))
            fout.write('        /cryostor2/appion/      :      {}\n'.format(bytes_to_string(temp_dict['tot_appion_size'][1])))
            fout.write('        /cryostor2/frames/      :      {}\n'.format(bytes_to_string(temp_dict['tot_frames_size'][1])))
            fout.write('      Total Size on cryostor3   :    {}\n'.format(bytes_to_string(temp_dict['tot_size'][2])))
            fout.write('        /cryostor3/leginon/     :      {}\n'.format(bytes_to_string(temp_dict['tot_leginon_size'][2])))
            fout.write('        /cryostor3/appion/      :      {}\n'.format(bytes_to_string(temp_dict['tot_appion_size'][2])))
            fout.write('        /cryostor3/frames/      :      {}\n'.format(bytes_to_string(temp_dict['tot_frames_size'][2])))
            if temp_dict['tot_size'][0] > 0:
                fout.write('      cryostor1:\n')
                fout.write('        {:25s} {:25s} {:25s} {:25s} {}\n'.format('Session Name','Total Size on cryostor1','/cryostor1/../leginon/','/cryostor1/../appion/','/cryostor1/../frames/'))
                for i in range(len(temp_dict['sessions'])):
                    if (temp_dict['combined'][i][0] > 0) or show_all:
                        sesh = temp_dict['sessions'][i]
                        sesh_trunc = sesh[:20] + '...' if len(sesh) > 19 else sesh
                        fout.write('        {:25s} {:25s} {:25s} {:25s} {}\n'.format(sesh_trunc,bytes_to_string(temp_dict['combined'][i][0]),bytes_to_string(temp_dict['leginon'][i][0]),bytes_to_string(temp_dict['appion'][i][0]),bytes_to_string(temp_dict['frames'][i][0])))

            if temp_dict['tot_size'][1] > 0:
                fout.write('      cryostor2:\n')
                fout.write('        {:25s} {:25s} {:25s} {:25s} {}\n'.format('Session Name','Total Size on cryostor2','/cryostor2/leginon/','/cryostor2/appion/','/cryostor2/frames/'))
                for i in range(len(temp_dict['sessions'])):
                    if (temp_dict['combined'][i][1] > 0) or show_all:
                        sesh = temp_dict['sessions'][i]
                        sesh_trunc = sesh[:15] + '...' if len(sesh) > 14 else sesh
                        fout.write('        {:25s} {:25s} {:25s} {:25s} {}\n'.format(sesh_trunc,bytes_to_string(temp_dict['combined'][i][1]),bytes_to_string(temp_dict['leginon'][i][1]),bytes_to_string(temp_dict['appion'][i][1]),bytes_to_string(temp_dict['frames'][i][1])))

            if temp_dict['tot_size'][2] > 0:
                fout.write('      cryostor3:\n')
                fout.write('        {:25s} {:25s} {:25s} {:25s} {}\n'.format('Session Name','Total Size on cryostor3','/cryostor3/leginon/','/cryostor3/appion/','/cryostor3/frames/'))
                for i in range(len(temp_dict['sessions'])):
                    if (temp_dict['combined'][i][2] > 0) or show_all:
                        sesh = temp_dict['sessions'][i]
                        sesh_trunc = sesh[:15] + '...' if len(sesh) > 14 else sesh
                        fout.write('        {:25s} {:25s} {:25s} {:25s} {}\n'.format(sesh_trunc,bytes_to_string(temp_dict['combined'][i][2]),bytes_to_string(temp_dict['leginon'][i][2]),bytes_to_string(temp_dict['appion'][i][2]),bytes_to_string(temp_dict['frames'][i][2])))
            fout.write('\n\n')










if __name__ == "__main__":
    main()
