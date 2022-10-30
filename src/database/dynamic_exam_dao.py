import numpy as np

# Local imports
from src.database.connection import Connection
from src.models.dynamic_exam import DynamicExam
import src.utilities.utils as Utils

np.set_printoptions(threshold=np.inf)


class DynamicExamDao():
    """
    This class communicates Ethel's database to create, read and update exams

    Attributes
    ----------
    database : str
            Path to the database
    """

    def __init__(self, database='src/database/ethel.db'):
        self.__c = Connection()
        self.__db = database

    @property
    def c(self):
        return self.__c

    @property
    def db(self):
        return self.__db

    def create_exam(self, exam: DynamicExam):
        '''
        This method creates a new exam into Ethel's database.

        Parameters
        ----------
        exam : DynamicExam
                The exam data

        Returns
        -------
        bool
                Whether the operation was successful or not
        '''
        result = False
        sql = 'SELECT COUNT(*)+1 FROM dynamic_exams'
        sql_ = 'INSERT INTO dynamic_exams (dyn_ex_cop_x, dyn_ex_cop_y, dyn_ex_date, pat_cod, usr_cod) values (?,?,?,?,?)'
        cop_x = Utils.cop_to_str(exam.cop_x)
        cop_y = Utils.cop_to_str(exam.cop_y)
        date = Utils.datetime_to_str(exam.date)
        try:
            self.c.connect(self.db)
            cursor = self.c.conn.execute(sql)
            exam.cod = cursor.fetchone()[0]
            self.c.conn.execute(
                sql_, [cop_x, cop_y, date, exam.pat_cod, exam.usr_cod])
            self.c.conn.commit()
            result = True
        except:
            print("Error!")
        finally:
            self.c.close()
        return result

    def read_exam(self, ex_cod: int):
        '''
        This method reads an existent exam from Ethel's database.

        Parameters
        ----------
        ex_cod : int
                The exam code

        Returns
        -------
        False or DynamicExam
                Whether the operation was successful or not
        '''
        exam = False
        sql = 'SELECT dyn_ex_cop_x, dyn_ex_cop_y, dyn_ex_date, pat_cod, usr_cod FROM dynamic_exams WHERE dyn_ex_cod = ?'
        try:
            self.c.connect(self.db)
            cursor = self.c.conn.execute(sql, [ex_cod])
            result = cursor.fetchone()
            if result:
                cop_x = Utils.str_to_cop(result[0])
                cop_y = Utils.str_to_cop(result[1])
                date = Utils.str_to_datetime(result[2])
                exam = DynamicExam(ex_cod, cop_x, cop_y,
                                   date, result[3], result[4])
        except:
            print("Error!")
        finally:
            self.c.close()
        return exam

    def update_exam(self, exam: DynamicExam):
        '''
        This method updates an existent exam into Ethel's database.

        Parameters
        ----------
        exam : DynamicExam
                The exam data

        Returns
        -------
        bool
                Whether the operation was successful or not
        '''
        result = False
        sql = 'UPDATE dynamic_exams SET dyn_ex_cop_x = ?, dyn_ex_cop_y = ?, dyn_ex_date = ?, pat_cod = ?, usr_cod = ? WHERE dyn_ex_cod = ?'
        try:
            self.c.connect(self.db)
            cop_x = Utils.cop_to_str(exam.aps)
            cop_y = Utils.cop_to_str(exam.mls)
            date = Utils.datetime_to_str(exam.date)
            self.c.conn.execute(
                sql, [cop_x, cop_y, date, exam.pat_cod, exam.usr_cod, exam.cod])
            self.c.conn.commit()
            result = True
        except:
            print("Error!")
        finally:
            self.c.close()
        return result

    def read_exams_from_patient(self, pat_cod: int):
        '''
        This method reads an existent exam from Ethel's database.

        Parameters
        ----------
        pat_cod : int
                The patient cod

        Returns
        -------
        bool or list
                Whether the operation was successful or not
        '''
        exams = list()
        sql = 'SELECT dyn_ex_cod, dyn_ex_cop_x, dyn_ex_cop_y, dyn_ex_date, usr_cod FROM dynamic_exams WHERE pat_cod = ?'
        try:
            self.c.connect(self.db)
            cursor = self.c.conn.execute(sql, [pat_cod])
            results = cursor.fetchall()
            if results:
                for result in results:
                    cop_x = Utils.str_to_cop(result[1])
                    cop_y = Utils.str_to_cop(result[2])
                    date = Utils.str_to_datetime(result[3])
                    exam = DynamicExam(
                        result[0], cop_x, cop_y, date, pat_cod, result[4])
                    exams.append(exam)
        except:
            print("Error!")
        finally:
            self.c.close()
        return exams

    def list_exams(self):
        '''
        This method lists all exams from Ethel's database.

        Returns
        -------
        bool or list
                Whether the operation was successful or not
        '''
        exams = False
        sql = 'SELECT dyn_ex_cod, dyn_ex_cop_x, dyn_ex_cop_y, dyn_ex_date, pat_cod, usr_cod FROM dynamic_exams'
        try:
            self.c.connect(self.db)
            cursor = self.c.conn.execute(sql)
            results = cursor.fetchall()
            if results:
                exams = list()
                for result in results:
                    cop_x = Utils.str_to_cop(result[1])
                    cop_y = Utils.str_to_cop(result[2])
                    date = Utils.str_to_datetime(result[3])
                    exam = DynamicExam(
                        result[0], cop_x, cop_y, date, result[4], result[5])
                    exams.append(exam)
        except:
            print("Error!")
        finally:
            self.c.close()
        return exams
