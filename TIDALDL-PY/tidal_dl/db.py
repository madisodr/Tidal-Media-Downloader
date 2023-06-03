#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   db.py
@Time    :   2023/6/1
@Author  :   madisodr
@Version :   1.0
@Contact :   drmadman92@gmail.com
@Desc    :   mysql database connector
'''

import mysql.connector

_connection = None

def getConnection():
    global _connection
    if not _connection:
        _connection =  mysql.connector.connect(
        host="localhost",
        user="root", # TODO make this a configuration option
        password="frepr2praw" # TODO make this a config option
    )
        
    return _connection