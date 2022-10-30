# Local imports
from src.database.connection import Connection
from src.models.patient import Patient
import src.utilities.utils as Utils


class PatientDao:
    """
    This class communicates Ethel's database to create, read and update patients

    Attributes
    ----------
    database : str
            Path to the database
    """

    def __init__(self, database="src/database/ethel.db"):
        self.__c = Connection()
        self.__db = database

    @property
    def c(self):
        return self.__c

    @property
    def db(self):
        return self.__db

    def create_patient(self, patient: Patient):
        """
        This method creates a new patient into Ethel's database.

        Parameters
        ----------
        patient : Patient
                The patient object

        Returns
        -------
        bool
                Whether the operation was successful or not
        """
        result = False
        sql = "SELECT COUNT(*)+1 FROM patients"
        sql_ = "INSERT INTO patients (pat_cod, pat_name, pat_sex, pat_birth, pat_height, pat_weight, pat_imc) values (?,?,?,?,?,?,?)"
        try:
            self.c.connect(self.db)
            cursor = self.c.conn.execute(sql)
            pat_cod = cursor.fetchone()[0]
            patient.cod = pat_cod
            pat_birth = Utils.date_to_str(patient.birth)
            self.c.conn.execute(
                sql_,
                [
                    patient.cod,
                    patient.name,
                    patient.sex,
                    pat_birth,
                    patient.height,
                    patient.weight,
                    patient.imc,
                ],
            )
            self.c.conn.commit()
            result = True
        except:
            print("Error!")
        finally:
            self.c.close()
        return result

    def read_patient(self, pat_cod: int):
        """
        This method reads an existent patient from Ethel's database.

        Parameters
        ----------
        pat_cod : int
                The patient code

        Returns
        -------
        False or patient
                Whether the operation was successful or not
        """
        patient = False
        sql = "SELECT pat_name, pat_sex, pat_birth, pat_height, pat_weight, pat_imc FROM patients WHERE pat_cod = ?"
        try:
            self.c.connect(self.db)
            cursor = self.c.conn.execute(sql, [pat_cod])
            result = cursor.fetchone()
            if result:
                pat_birth = Utils.str_to_date(result[2])
                patient = Patient(
                    pat_cod,
                    result[0],
                    result[1],
                    pat_birth,
                    result[3],
                    result[4],
                    result[5],
                )
        except:
            print("Error!")
        finally:
            self.c.close()
        return patient

    def update_patient(self, patient: Patient):
        """
        This method updates an existent patient into Ethel's database.

        Parameters
        ----------
        patient : Patient
                The patient object

        Returns
        -------
        bool
                Whether the operation was successful or not
        """
        result = False
        sql = "UPDATE patients SET pat_name = ?, pat_sex = ?, pat_birth = ?, pat_height = ?, pat_weight = ?, pat_imc = ? WHERE pat_cod = ?"
        try:
            self.c.connect(self.db)
            pat_birth = Utils.date_to_str(patient.birth)
            self.c.conn.execute(
                sql,
                [
                    patient.name,
                    patient.sex,
                    pat_birth,
                    patient.height,
                    patient.weight,
                    patient.imc,
                    patient.cod,
                ],
            )
            self.c.conn.commit()
            result = True
        except:
            print("Error!")
        finally:
            self.c.close()
        return result

    def list_patients(self):
        """
        This method lists all patients from Ethel's database.

        Returns
        -------
        bool or list
                Whether the operation was successful or not
        """
        patients = False
        sql = "SELECT pat_cod, pat_name, pat_sex, pat_birth, pat_height, pat_weight, pat_imc FROM patients"
        try:
            self.c.connect(self.db)
            cursor = self.c.conn.execute(sql)
            results = cursor.fetchall()
            if results:
                patients = list()
                for result in results:
                    pat_birth = Utils.str_to_date(result[3])
                    patient = Patient(
                        result[0],
                        result[1],
                        result[2],
                        pat_birth,
                        result[4],
                        result[5],
                        result[6],
                    )
                    patients.append(patient)
        except Exception as e:
            print("Error!", e)
        finally:
            self.c.close()
        return patients
