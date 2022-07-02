from __future__ import annotations

import sqlite3
import sshtunnel
import time
from typing import TypeVar, Callable, List


__T = TypeVar("__T")
__R = TypeVar("__R")


class DBCLiteServer:

    DBConfigsTuple = TypeVar('(host, user, password, database)')
    PathLikeStr = TypeVar("PathLike")
    __insert_clear = '''INSERT INTO {0} VALUES ({1})'''
    __insert_autoinc = '''INSERT INTO {0} VALUES (NULL, {1})'''
    __select = '''SELECT * FROM {0}'''

    def __init__(self, db_configs: DBConfigsTuple | PathLikeStr, use_ssh_tunnel: bool = False, **kwargs):
        self.__itable: str | None = None
        self.__has_first_autoinc: bool | None = None
        self.__slice: slice | None = None
        self.__type: Callable[[__T], __R] | None = None

        self.__use_ssh_tunnel: bool = use_ssh_tunnel
        self.__kwargs: dict = kwargs
        self.__ssh_tunnel: sshtunnel.SSHTunnelForwarder | None = None
        self.connection: sqlite3.Connection | None = None
        self.cursor: sqlite3.Cursor | None = None
        if isinstance(db_configs, tuple):
            self.db_config = dict(host=db_configs[0], user=db_configs[1], passwd=db_configs[2], db=db_configs[3])
            self.__check_connection = self.__check_remote_connection
            self.__init_remote_db_connection()
        else:
            self.db_config = dict(database=db_configs)
            self.__check_connection = self.__check_local_connection
            self.__init_local_db_connection()

    def create_tables(self, db_query: list) -> None:
        if self.cursor is None:
            raise Exception("Cursor is None!")
        for command in db_query:
            self.cursor.execute(command)

    def init_ssh_tunnel(self, ssh_host, ssh_port, ssh_user, ssh_password, remote_address, local_address) -> None:
        if self.__use_ssh_tunnel:
            raise Exception('You are not use SSH tunnel!')
        self.__ssh_tunnel = sshtunnel.SSHTunnelForwarder((ssh_host, ssh_port),
                                                         ssh_username=ssh_user,
                                                         ssh_password=ssh_password,
                                                         remote_bind_address=(remote_address, 3306),
                                                         local_bind_address=(
                                                         local_address, 3306))  # debug_level='TRACE',

    def __init_local_db_connection(self):
        sqlite3.enable_callback_tracebacks(True)
        self.connection = sqlite3.connect(**self.db_config, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.connection.text_factory = str
        self.cursor = self.connection.cursor()

    def __init_remote_db_connection(self):
        if self.__use_ssh_tunnel and not self.__ssh_tunnel:
            raise Exception('You have not init ssh tunnel yet. Call `init_ssh_tunnel(...)` firstly!')
        import MySQLdb
        self.connection = MySQLdb.connect(**self.db_config, **self.__kwargs)
        self.cursor = self.connection.cursor()

    def __check_local_connection(self):
        return

    def __check_remote_connection(self) -> None:
        if self.connection is None:
            raise Exception('You have not init db connection yet. Call `init_db_connection(...)` firstly!')
        if not self.connection.open:  # Why "Unresolved attribute reference 'open' for class 'Connection'"
            self.__init_remote_db_connection()

    def table(self, table_name: str) -> DBCLiteServer:
        self.__itable = table_name
        return self

    def i(self, _slice: slice) -> DBCLiteServer:
        self.__slice = _slice
        return self

    def row_view(self, row_type_func: Callable[[__T], __R] = lambda x: x) -> DBCLiteServer:
        self.__type = row_type_func
        return self

    def has_auto_inc(self, bool_has_auto_inc: bool) -> DBCLiteServer:
        self.__has_first_autoinc = bool_has_auto_inc
        return self

    # def add_configuration(self, table_name, use_id=True, order_by_id='ID'):
    #     if use_id:
    #         self._configurations[table_name]['insert'] = 'INSERT INTO {0} VALUES (NULL, {1})'
    #     else:
    #         self._configurations[table_name]['insert'] = 'INSERT INTO {0} VALUES ({1})'
    #     if use_id and order_by_id:
    #         self._configurations[table_name]['select'] = 'SELECT * FROM {0} ORDER BY ID'
    #     else:
    #         self._configurations[table_name]['select'] = 'SELECT * FROM {0}'

    def read(self, own: str, *args) -> List:
        self.__check_connection()
        own_command = self.__select.format(own) if len(own.split()) == 1 else own
        print(time.ctime(), own_command, args)
        self.cursor.execute(own_command, args)
        return self.__close_connection()

    def add(self, *args) -> List:
        assert self.__itable, 'Add table name to the params!'
        self.__check_connection()
        if self.__has_first_autoinc:
            own_command = self.__insert_autoinc.format(self.__itable, ','.join(len(args) * '?'))
        else:
            own_command = self.__insert_clear.format(self.__itable, ','.join(len(args) * '?'))
        print(time.ctime(), own_command, args)
        self.cursor.execute(own_command, args)
        return self.__close_connection(True)

    def execute(self, own: str, *args) -> List:
        self.__check_connection()
        print(time.ctime(), own, args)
        self.cursor.execute(own, args)
        return self.__close_connection()

    def add_sql_function(self, func_name, num_args, func) -> None:
        self.connection.create_function(func_name, num_args, func)

    def revoke_params(self) -> None:
        self.__slice = None
        self.__itable = None
        self.__type = None
        self.__has_first_autoinc = None

    def __close_connection(self, was_add_last: bool = False) -> List:
        result = self.cursor.fetchall()
        if self.__type:
            result = list(map(self.__type, result))
        if self.__slice is not None:
            result = [item[self.__slice] for item in result]
        self.revoke_params()
        self.connection.commit()
        if was_add_last:
            return self.cursor.lastrowid
        return result

