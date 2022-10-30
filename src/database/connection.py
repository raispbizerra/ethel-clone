# Standard library imports
from os import system as bash
import sqlite3


class Connection():
    '''
    A class that represents ETHEL's database connection
    '''

    def __init__(self):
        self.__conn = None

    @property
    def conn(self):
        return self.__conn

    def connect(self, database='src/database/ethel.db'):
        '''A method to open the connection'''
        self.__conn = sqlite3.connect(database)

    def close(self):
        '''A method to close the connection'''
        self.__conn.close()

    def redefine(self, database):
        '''A method to redefine database

        Arguments
        ---------
        database: str
            Database to be redefined        
        '''

        bash(f"rm {database}")
        bash(f"sqlite3 {database} < src/database/scripts.sql")
