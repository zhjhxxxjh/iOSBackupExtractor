# -*- coding: utf-8 -*-
"""
    This module implements extract iOS backup file.
    :copyright: (c) 2016 by yiwangwuqian.
"""

__VERSION__ = 0.1

import sys
import os
import shutil

import mbdbls
import manifest_db
import backup_device_info

current_dir = os.path.split(os.path.abspath(__file__))[0]
current_dir = current_dir + '/'

'Extract files from iOS iTunes backup directories'


class Extractor(object):
    pass

'''General about'''


def move_file(file_path, new_file_name):
    '''directory setup'''
    (dir_path, file_name) = os.path.split(new_file_name)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    '''file move'''
    if file_name != None and file_name != '':
        shutil.copy(file_path, new_file_name)
    print new_file_name

'''App about'''
APP_DOMAIN_PREFIX = 'AppDomain-'


class AppExtractor(Extractor):

    '''iOS9 differ with iOS10'''
    def backup_file_path(self,fileID):
        path = None
        if self.os_version[:2] == '10':
            middle_appended_path = os.path.join(self.backup_base_path, fileID[:2])
            path = os.path.join(middle_appended_path, fileID) 
        else:
            path = os.path.join(self.backup_base_path, fileID)
        return path

    def start_extract(self, *args, **kwargs):
        self.backup_base_path = args[0]
        self.extract_bundleid = args[1]
        self.os_version = kwargs.get('os_version','')
        self.output_dir = kwargs.get('output_dir', current_dir)
        self.done_callback = kwargs.get('done_callback', None)
        self.app_extract()

    def app_extract_ergodic(self, *args):
        dict = args[0]
        domain = dict['domain']
        fileID = dict['fileID']
        filename = dict['filename']

        if domain.find(APP_DOMAIN_PREFIX) == 0:
            a_bundle_id = domain[len(APP_DOMAIN_PREFIX):]
            file_path = self.backup_file_path(fileID)
            if (a_bundle_id == self.extract_bundleid) and (os.path.exists(file_path) == True):
                new_file_name = os.path.join(os.path.join(
                    self.output_dir, a_bundle_id), filename)
                move_file(file_path, new_file_name)

    def app_extract(self):
        if self.os_version[:2] == '10':
            extern_extract_func = manifest_db.extern_run
        else:
            extern_extract_func = mbdbls.extern_run

        extern_extract_func(self.backup_base_path, self.app_extract_ergodic)
        if self.done_callback != None:
            self.done_callback()

'''By main execute about'''


def device_select_input_interaction(device_list):
    device_select_show_text = '------device names------\n'
    for i in range(0, len(device_list)):
        device = device_list[i]
        a_device_name = device[1][0]
        device_select_show_text += '%d| %s' % (i,
                                               a_device_name.encode('utf-8') + '\n')
    device_select_show_text += "please input index: "
    input_device = raw_input(device_select_show_text)
    if input_device.isdigit():
        if int(input_device) >= len(device_list):
            print "please input valid index!"
            return None
        else:
            return int(input_device)
    else:
        print "please input integer!"
        return None


def bundleid_select_input_interaction(list):
    bundleid_select_show_text = '------bundle ids------\n'
    for i in range(0, len(list)):
        bundleid = list[i]
        bundleid_select_show_text += '%d| %s' % (i, list[i] + '\n')
    bundleid_select_show_text += "please input index: "
    input_bundleid = raw_input(bundleid_select_show_text)
    if input_bundleid.isdigit():
        if int(input_bundleid) >= len(list):
            print "please input valid index!"
            return None
        else:
            bundleid = list[int(input_bundleid)]
            return bundleid
    else:
        print "please input integer!"
        return None


def output_dir_input_interaction():
    input_path = raw_input("please set output dir path: ")
    if input_path and not os.path.exists(input_path) and not os.path.isfile(input_path):
        input_path += '/'

    if input_path and os.path.exists(input_path) and os.path.isdir(input_path):
        return input_path
    else:
        print "please input valid path!"
        return None


def extract_done_callback(*args):
    print 'extract is done'

if __name__ == '__main__':
    device_list = backup_device_info.backup_dir_device_list()
    selected_device_index =  device_select_input_interaction(device_list)        
    selected_dir_path = device_list[selected_device_index][0]
    selected_device_version = device_list[selected_device_index][1][1]
    if selected_dir_path != None:
        bundleid_list = backup_device_info.device_installed_app_list(selected_dir_path)
        once_selected_bundleid = bundleid_select_input_interaction(bundleid_list)
        if once_selected_bundleid != None:
            output_dir = output_dir_input_interaction()
            if output_dir != None:
                extractor = AppExtractor()
                kw_params = {'done_callback' : extract_done_callback,'output_dir' :output_dir, 'os_version' : selected_device_version}
                extractor.start_extract(selected_dir_path, once_selected_bundleid, **kw_params)
