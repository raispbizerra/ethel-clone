# Local imports
from src.database.connection import Connection
from src.models.user import User
import src.utilities.utils as Utils


class UserDao:
    """
    This class communicates Ethel's database to create, read and update users

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

    def create_user(self, user: User):
        """
        This method creates a new User into Ethel's database.

        Parameters
        ----------
        user : User
                The User object

        Returns
        -------
        bool
                Whether the operation was successful or not
        """
        result = False
        sql = "INSERT INTO users (usr_name, usr_username, usr_password, usr_email, usr_is_adm) values (?,?,?,?,?)"
        try:
            self.c.connect(self.db)
            self.c.conn.execute(
                sql,
                [
                    user.get_name(),
                    user.get_username(),
                    user.get_password(),
                    user.get_email(),
                    user.get_is_adm(),
                ],
            )
            self.c.conn.commit()
            result = True
        except:
            print("Error!")
        finally:
            self.c.close()
        return result

    def read_user(self, usr_username: str, usr_password: str):
        """
        This method reads an existent User from Ethel's database.

        Parameters
        ----------
        usr_username : str
                The user username
        usr_password : str
                The user password

        Returns
        -------
        False or User
                Whether the operation was successful or not
        """
        user = False
        sql = "SELECT usr_cod, usr_name, usr_email, usr_is_adm FROM users WHERE usr_username = ? AND usr_password = ?"
        try:
            self.c.connect(self.db)
            cursor = self.c.conn.execute(sql, [usr_username, usr_password])
            result = cursor.fetchone()
            if result:
                user = User(
                    result[0],
                    result[1],
                    usr_username,
                    usr_password,
                    result[2],
                    result[3],
                )
        except:
            print("Error!")
        finally:
            self.c.close()
        return user

    def update_user(self, user: User):
        """
        This method updates an existent User into Ethel's database.

        Parameters
        ----------
        user : User
                The User object

        Returns
        -------
        bool
                Whether the operation was successful or not
        """
        result = False
        sql = "UPDATE users SET usr_name = ?, usr_username = ?, usr_password = ?, usr_email = ?, usr_is_adm = ? WHERE usr_cod = ?"
        try:
            self.c.connect(self.db)
            self.c.conn.execute(
                sql,
                [
                    user.get_name(),
                    user.get_username(),
                    user.get_password(),
                    user.get_email(),
                    user.get_is_adm(),
                    user.get_cod(),
                ],
            )
            self.c.conn.commit()
            result = True
        except:
            print("Error!")
        finally:
            self.c.close()
        return result

    def list_users(self):
        """
        This method lists all users from Ethel's database.

        Returns
        -------
        bool or list
                Whether the operation was successful or not
        """
        users = False
        sql = "SELECT usr_cod, usr_name, usr_username, usr_password, usr_email, usr_is_adm FROM users"
        try:
            self.c.connect(self.db)
            cursor = self.c.conn.execute(sql)
            results = cursor.fetchall()
            if results:
                users = list()
                for result in results:
                    user = User(
                        result[0], result[1], result[2], result[3], result[4], result[5]
                    )
                    users.append(user)
        except:
            print("Error!")
        finally:
            self.c.close()
        return users
