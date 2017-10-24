# -- coding: utf8 --

try:
	from setuptools import setup
except:
	from distutils import setup

import exercise47
import os

def getSubpackages(name):
    """获取该模块下所有的子模块名称"""
    splist = []

    for dirpath, _dirnames, _filenames in os.walk(name):
        if os.path.isfile(os.path.join(dirpath, '__init__.py')):
            splist.append(".".join(dirpath.split(os.sep)))
    return splist

config = {
	'description':'My Project',
	'author':exercise47.author,
	'url':'http://www.vnpy.org',
	'download_url':'www.baidu.com',
	'author_email':'lo-e@outlook.com',
	'version':exercise47.version,
	#'install_requires':['nothing'],
	'packages':getSubpackages('NAME'),
	#'scripts':[],
	'name':'exercise_46'
}

setup(**config)