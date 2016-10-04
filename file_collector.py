"""
Module for collection files with given extensions.
"""

from __future__ import print_function
import os
import yaml

from fnmatch import fnmatch

class FileContent(object):
    """Container class, stores properties for given file. """
    def __init__(self, path, parse_fn=None):
        self._path = path
        self._base_name = None
        self._dir_name = None
        self._content = None
        self._parsed_content = None
        self._parse_fn = parse_fn if parse_fn else lambda x: None

    @property
    def base_name(self):
        """Returns _base_name attribute."""
        self._get_base_name()
        return self._base_name

    @property
    def dir_name(self):
        """Returns _dir_name attribute."""
        self._get_dir_name()
        return self._dir_name

    @property
    def content(self):
        """Returns _content attribute."""
        self._get_content()
        return self._content

    @property
    def parsed(self):
        """Returns _parsed_content attribute."""
        self._get_dict()
        return self._parsed_content

    def _get_base_name(self):
        """Assigns _base_name attribute."""
        self._base_name = os.path.basename(self._path)

    def _get_dir_name(self):
        """Assigns _dir_name attribute."""
        self._dir_name = os.path.dirname(self._path)

    def _get_content(self):
        """Assigns _content attribute with given file content."""
        with open(self._path, 'r') as fhl:
            self._content = fhl.read()

    def _get_dict(self):
        """Assigns to _parsed_content YAML content."""
        self._parsed_content = self._parse_fn(self.content)


def check_meta(file_content, options):
    """Check if given tag is in current file and adds FileContent object."""
    if options['tags'] == [None]:
        return True
    for elm in file_content:
        if 'meta' in elm:
            for tag in elm['meta'].get('tags', []):
                if tag in options['tags']:
                    return True
    return False


class FileCollector(object):
    """
    Class that collects files with given extensions
    """

    def __init__(self, extensions, paths, filter_fn=None, parse_fn=None, options=None):
        self._extensions = extensions
        self._paths = paths
        self._results = list()
        self._filter_fn = filter_fn if filter_fn else lambda x, y: True
        self._parse_fn = parse_fn if parse_fn else lambda x: None
        self._options = options

    @property
    def results(self):
        """Returns _results attribute."""
        return self._results

    def _walk(self, path):
        """Method that searches for given extensions and collects their abs path and filename in list."""
        for path, subdirs, files in os.walk(path):       #pylint: disable=unused-variable
            for name in files:
                if any((fnmatch(name, pattern) for pattern in self._extensions)):
                    result_dir = os.path.abspath(os.path.join(path))
                    curr_file = os.path.join(result_dir, name)
                    file_cont = FileContent(curr_file, self._parse_fn)
                    if self._filter_fn(file_cont.parsed, self._options):
                        self._results.append(file_cont)

    def _single_file(self, file):
        """Adds FileContent object of a single file to results attr."""
        self._results.append(FileContent(file))

    def iterator(self):
        """ Calls for private method _walk and returns list of tuples (path, filename)"""
        for path in self._paths:
            if os.path.isfile(path):
                self._single_file(path)
            if os.path.isdir(path):
                self._walk(path)
        return self._results


#_____________________________________________________________________________
# UNIT-TEST SECTION BELOW
# pylint: disable=line-too-long,missing-docstring,no-self-use,protected-access

import unittest
import shutil


YAML_TEST = """
            - meta:
                 tags: ['smoke']"""


class TestFileContent(unittest.TestCase):
  
    DIR = './tmp'
    MY_DIR = 'mydir'
    FILE_1 = 'firstfile.yaml'
    FILE_2 = 'secondfile.yml'
    FILE_3 = 'thirdfile.yaml'
    CURR_DIR = os.path.dirname(os.path.abspath(__file__))
  
    def setUp(self):
        self.maxDiff = None     #pylint: disable=invalid-name
        if os.path.exists(self.DIR):
            shutil.rmtree(self.DIR)
        os.mkdir(self.DIR)
        my_dir = os.path.join(self.DIR, self.MY_DIR)
        os.mkdir(my_dir)
        file_1 = os.path.join(self.DIR, self.FILE_1)
        file_2 = os.path.join(my_dir, self.FILE_2)
        file_3 = os.path.join(self.DIR, self.FILE_3)
        with open(file_1, 'w') as fhl:
            fhl.write('File1')
        with open(file_2, 'w') as fhl:
            fhl.write('File2')
        with open(file_3, 'w') as fhl:
            fhl.write(YAML_TEST)
  
    def tearDown(self):
        if os.path.exists(self.DIR):
            shutil.rmtree(self.DIR)

    def test_basic(self):
        path = os.path.normpath(os.path.join(self.CURR_DIR, self.DIR, self.FILE_1))
        FileContent(path)
  
    def test_base_name(self):
        path = os.path.normpath(os.path.join(self.CURR_DIR, self.DIR, self.FILE_1))
        file_cont = FileContent(path)
        self.assertEqual('firstfile.yaml', file_cont.base_name)
  
    def test_base_name_fail(self):
        path = os.path.normpath(os.path.join(self.CURR_DIR, self.DIR, self.FILE_1))
        file_cont = FileContent(path)
        self.assertNotEqual(path, file_cont.base_name)
  
    def test_dir_name_fails(self):
        path = os.path.normpath(os.path.join(self.CURR_DIR, self.DIR, self.FILE_1))
        file_cont = FileContent(path)
        self.assertNotEqual(path, file_cont.dir_name)
  
    def test_content(self):
        path = os.path.normpath(os.path.join(self.CURR_DIR, self.DIR, self.FILE_1))
        file_cont = FileContent(path)
        self.assertEqual('File1', file_cont.content)
  
    def test_content_fails(self):
        path = os.path.normpath(os.path.join(self.CURR_DIR, self.DIR, self.FILE_1))
        file_cont = FileContent(path)
        self.assertNotEqual('File2', file_cont.content)
  
    def test_content_fails_no_fail(self):
        path = os.path.normpath(os.path.join(self.CURR_DIR, self.DIR, 'wrong.txt'))
        file_cont = FileContent(path)
        try:
            file_cont.content
        except IOError:
            pass
        else:
            self.fail('No IOError was raised.')
  
    def test_as_dict(self):
        path = os.path.normpath(os.path.join(self.CURR_DIR, self.DIR, self.FILE_3))
        file_cont = FileContent(path, yaml.load)
        self.assertEqual([{'meta': {'tags': ['smoke']}}], file_cont.parsed)
  
    def test_as_dict_fail(self):
        path = os.path.normpath(os.path.join(self.CURR_DIR, self.DIR, self.FILE_1))
        file_cont = FileContent(path)
        self.assertNotEqual('wrong', file_cont.parsed)


class TestFileCollector(unittest.TestCase):
 
    DIR = './tmp'
    MY_DIR = 'mydir'
    FILE_1 = 'firstfile.yaml'
    FILE_2 = 'secondfile.yml'
    FILE_3 = 'thirdfile.txt'
    CURR_DIR = os.path.dirname(os.path.abspath(__file__))
 
    def setUp(self):
        self.maxDiff = None     #pylint: disable=invalid-name
        if os.path.exists(self.DIR):
            shutil.rmtree(self.DIR)
        os.mkdir(self.DIR)
        my_dir = os.path.join(self.DIR, self.MY_DIR)
        os.mkdir(my_dir)
        file_1 = os.path.join(self.DIR, self.FILE_1)
        file_2 = os.path.join(my_dir, self.FILE_2)
        file_3 = os.path.join(my_dir, self.FILE_3)
        with open(file_1, 'w') as fhl:
            fhl.write('temp file 1 for testing')
        with open(file_2, 'w') as fhl:
            fhl.write(YAML_TEST)
        with open(file_3, 'w') as fhl:
            fhl.write('temp file 3 for testing')
 
    def tearDown(self):
        if os.path.exists(self.DIR):
            shutil.rmtree(self.DIR)
 
    def test_creation(self):
        extensions = ('*.yaml', '*.yml')
        paths = ('./tmp',)
        FileCollector(extensions, paths)
  
    def test_creation_with_mata(self):
        extensions = ('*.yaml', '*.yml')
        paths = ('./tmp',)
        options = dict()
        options['tags'] = 'meta'
        FileCollector(extensions, paths, options)
 
    def test_iterator(self):
        extensions = ('*.yaml', '*.yml')
        paths = ('tmp',)
        fcoll = FileCollector(extensions, paths)
        result = list(fcoll.iterator())
        self.assertEqual('firstfile.yaml', result[0].base_name)
        self.assertEqual('secondfile.yml', result[1].base_name)

    def test_iterator_no_tag_options(self):
        extensions = ('*.yaml', '*.yml')
        paths = ('tmp',)
        options = dict()
        options['tags'] = [None]
        fcoll = FileCollector(extensions, paths, filter_fn=check_meta, parse_fn=yaml.load, options=options)
        result = list(fcoll.iterator())
        self.assertEqual('firstfile.yaml', result[0].base_name)
        self.assertEqual('secondfile.yml', result[1].base_name)

    def test_iterator_with_meta(self):
        extensions = ('*.yaml', '*.yml')
        paths = ('tmp',)
        options = dict()
        options['tags'] = 'smoke'
        fcoll = FileCollector(extensions, paths, filter_fn=check_meta, parse_fn=yaml.load, options=options)
        fcoll.iterator()
        available = fcoll.results
        self.assertEqual('secondfile.yml', available[0].base_name)
 
    def test_iterator_with_meta_fail(self):
        extensions = ('*.yaml', '*.yml')
        paths = ('tmp',)
        options = dict()
        options['tags'] = 'temp file 3 for testing'
        fcoll = FileCollector(extensions, paths, filter_fn=check_meta, parse_fn=yaml.load, options=options)
        fcoll.iterator()
        available = fcoll.results
        self.assertEqual([], available)
  
if __name__ == "__main__":
    unittest.main()
