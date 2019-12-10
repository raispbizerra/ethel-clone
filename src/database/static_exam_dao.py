# Local imports
from src.database.connection import Connection
from src.models.static_exam import StaticExam
import src.utilities.utils as Utils
import datetime as dt

class StaticExamDao():
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

    def create_exam(self, exam: StaticExam):
        '''
        This method creates a new exam into Ethel's database.

        Parameters
        ----------
        exam : StaticExam
                The exam data

        Returns
        -------
        bool
                Whether the operation was successful or not
        '''
        result = False
        sql = 'INSERT INTO static_exams (sta_ex_aps, sta_ex_mls, sta_ex_date, sta_ex_type, pat_cod, usr_cod) values (?,?,?,?,?,?)'
        sta_ex_aps = Utils.list_to_str(exam.aps)
        sta_ex_mls = Utils.list_to_str(exam.mls)
        # sta_ex_date = Utils.datetime_to_str(exam.date)
        try:
            self.c.connect(self.db)
            self.c.conn.execute(sql, [sta_ex_aps, sta_ex_mls, exam.date, exam.state, 
                exam.pat_cod, exam.usr_cod])
            self.c.conn.commit()
            result = True
        except Exception as e:
            print(f"Error! {e}")
        finally:
            self.c.close()
        return result

    def read_exam(self, sta_ex_cod: int):
        '''
        This method reads an existent exam from Ethel's database.

        Parameters
        ----------
        sta_ex_cod : int
                The exam code

        Returns
        -------
        False or StaticExam
                Whether the operation was successful or not
        '''
        exam = False
        sql = 'SELECT sta_ex_aps, sta_ex_mls, sta_ex_date, sta_ex_type, pat_cod, usr_cod FROM static_exams WHERE sta_ex_cod = ?'
        try:
            self.c.connect(self.db)
            cursor = self.c.conn.execute(sql, [sta_ex_cod])
            result = cursor.fetchone()
            if result:
                sta_ex_aps = Utils.str_to_array(result[0])
                sta_ex_mls = Utils.str_to_array(result[1])
                # sta_ex_date = Utils.str_to_datetime(result[2])
                sta_ex_date = dt.datetime.strptime(result[2], '%d-%m-%Y %H:%M:%S.%f')
                exam = StaticExam(sta_ex_cod, sta_ex_aps, sta_ex_mls,
                                  sta_ex_date, result[3], result[4], result[5])
        except Exception as e:
            print("Error!", e)
        finally:
            self.c.close()
        return exam

    def update_exam(self, exam: StaticExam):
        '''
        This method updates an existent exam into Ethel's database.

        Parameters
        ----------
        exam : StaticExam
                The exam data

        Returns
        -------
        bool
                Whether the operation was successful or not
        '''
        result = False
        sql = 'UPDATE static_exams SET sta_ex_aps = ?, sta_ex_mls = ?, sta_ex_date = ?, sta_ex_type = ?, pat_cod = ?, usr_cod = ? WHERE sta_ex_cod = ?'
        try:
            self.c.connect(self.db)
            sta_ex_aps = Utils.list_to_str(exam.aps)
            sta_ex_mls = Utils.list_to_str(exam.mls)
            sta_ex_date = Utils.datetime_to_str(exam.date)
            self.c.conn.execute(sql, [sta_ex_aps, sta_ex_mls, sta_ex_date, exam.state,
                exam.pat_cod, exam.usr_cod, exam.cod])
            self.c.conn.commit()
            result = True
        except Exception as e:
            print("Error!", e)
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
        sql = 'SELECT sta_ex_cod, sta_ex_aps, sta_ex_mls, sta_ex_date, sta_ex_type, usr_cod FROM static_exams WHERE pat_cod = ?'
        try:
            self.c.connect(self.db)
            cursor = self.c.conn.execute(sql, [pat_cod])
            results = cursor.fetchall()
            if results:
                for result in results:
                    sta_ex_aps = Utils.str_to_array(result[1])
                    sta_ex_mls = Utils.str_to_array(result[2])
                    # sta_ex_date = Utils.str_to_datetime(result[3])
                    sta_ex_date = dt.datetime.strptime(result[3], '%d-%m-%Y %H:%M:%S.%f')
                    exam = StaticExam(
                        result[0], sta_ex_aps, sta_ex_mls, sta_ex_date, result[4], pat_cod, result[5])
                    exams.append(exam)
        except Exception as e:
            print("Error!", e)
        finally:
            self.c.close()
        return exams

    def read_last_exams_from_patient(self, pat_cod: int):
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
        sql = 'SELECT sta_ex_cod, sta_ex_aps, sta_ex_mls, sta_ex_date, sta_ex_type, usr_cod FROM static_exams WHERE sta_ex_type == "ON" AND pat_cod == ? ORDER BY sta_ex_date DESC LIMIT 3'
        try:
            self.c.connect(self.db)
            cursor = self.c.conn.execute(sql, [pat_cod])
            results = cursor.fetchall()
            if results:
                for result in results:
                    sta_ex_aps = Utils.str_to_array(result[1])
                    sta_ex_mls = Utils.str_to_array(result[2])
                    sta_ex_date = Utils.str_to_datetime(result[3])
                    exam = StaticExam(
                        result[0], sta_ex_aps, sta_ex_mls, sta_ex_date, result[4], pat_cod, result[5])
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
        sql = 'SELECT sta_ex_cod, sta_ex_aps, sta_ex_mls, sta_ex_date, sta_ex_type, pat_cod, usr_cod FROM static_exams'
        try:
            self.c.connect(self.db)
            cursor = self.c.conn.execute(sql)
            results = cursor.fetchall()
            if results:
                exams = list()
                for result in results:
                    sta_ex_aps = Utils.str_to_array(result[1])
                    sta_ex_mls = Utils.str_to_array(result[2])
                    # sta_ex_date = Utils.str_to_datetime(result[3])
                    sta_ex_date = dt.datetime.strptime(result[3], '%d-%m-%Y %H:%M:%S').strftime('%d-%m-%Y %H:%M:%S')
                    exam = StaticExam(
                        result[0], sta_ex_aps, sta_ex_mls, sta_ex_date, result[4], result[5], result[6])
                    exams.append(exam)
        except:
            print("Error!")
        finally:
            self.c.close()
        return exams

    def check(self, pat_cod: int, condition : str):
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
        sql = 'SELECT sta_ex_cod, sta_ex_aps, sta_ex_mls, sta_ex_date, sta_ex_type, usr_cod FROM static_exams WHERE pat_cod = ? AND sta_ex_type = ? ORDER BY sta_ex_date DESC'
        try:
            self.c.connect(self.db)
            cursor = self.c.conn.execute(sql, [pat_cod, condition])
            results = cursor.fetchall()
            if results:
                for result in results:
                    sta_ex_aps = Utils.str_to_array(result[1])
                    sta_ex_mls = Utils.str_to_array(result[2])
                    sta_ex_date = Utils.str_to_datetime(result[3])
                    exam = StaticExam(
                        result[0], sta_ex_aps, sta_ex_mls, sta_ex_date, result[4], pat_cod, result[5])
                    exams.append(exam)
        except:
            print("Error!")
        finally:
            self.c.close()
        return exams