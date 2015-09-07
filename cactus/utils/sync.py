#! /usr/bin/python
# Dispatch - synchronize two folders
from __future__ import print_function

import os
import filecmp
import shutil

from stat import *


class Dispatch:
    ''' This class represents a synchronization object '''

    def __init__(self, name=''):
        self.name = name
        self.node_list = []
        self.file_copied_count = 0
        self.folder_copied_count = 0

    def add_node(self, node):
        self.node_list.append(node)

    def compare_nodes(self):
        ''' This method takes the nodes in the node_list and compares them '''
        # For each node in the list
        for node in self.node_list:
            # If the list has another item after it, compare them
            if self.node_list.index(node) < len(self.node_list) - 1:
                node2 = self.node_list[self.node_list.index(node) + 1]
                print('\nComparing Node ' + str(self.node_list.index(node)) + ' and Node ' + str(self.node_list.index(node) + 1) + ':')
                # Passes the two root directories of the nodes to the recursive _compare_directories.
                self._compare_directories(node.root_path, node2.root_path)

    def _compare_directories(self, left, right):
        ''' This method compares directories. If there is a common directory, the
            algorithm must compare what is inside of the directory by calling this
            recursively.
        '''
        comparison = filecmp.dircmp(left, right)
        if comparison.common_dirs:
            for d in comparison.common_dirs:
                self._compare_directories(os.path.join(left, d), os.path.join(right, d))
        if comparison.left_only:
            self._copy(comparison.left_only, left, right)
        if comparison.right_only:
            self._copy(comparison.right_only, right, left)
        left_newer = []
        right_newer = []
        if comparison.diff_files:
            for d in comparison.diff_files:
                l_modified = os.stat(os.path.join(left, d)).st_mtime
                r_modified = os.stat(os.path.join(right, d)).st_mtime
                if l_modified > r_modified:
                    left_newer.append(d)
                else:
                    right_newer.append(d)
        self._copy(left_newer, left, right)
        self._copy(right_newer, right, left)

    def _copy(self, file_list, src, dest):
        ''' This method copies a list of files from a source node to a destination node '''
        for f in file_list:
            srcpath = os.path.join(src, os.path.basename(f))
            if os.path.isdir(srcpath):
                shutil.copytree(srcpath, os.path.join(dest, os.path.basename(f)))
                self.folder_copied_count = self.folder_copied_count + 1
                print('Copied directory \"' + os.path.basename(srcpath) + '\" from \"' + os.path.dirname(srcpath) + '\" to \"' + dest + '\"')
            else:
                shutil.copy2(srcpath, dest)
                self.file_copied_count = self.file_copied_count + 1
                print('Copied \"' + os.path.basename(srcpath) + '\" from \"' + os.path.dirname(srcpath) + '\" to \"' + dest + '\"')


class Node:
    ''' This class represents a node in a dispatch synchronization '''
    def __init__(self, path, name=''):
        self.name = name
        self.root_path = os.path.abspath(path)
        self.file_list = os.listdir(self.root_path)


def syncFiles(src, dst):
    dispatch = Dispatch('dispatch')
    dispatch.add_node(Node(src, 'node1'))
    dispatch.add_node(Node(dst, 'node2'))
    dispatch.compare_nodes()
