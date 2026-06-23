
from web_socket.tool.log_tool import LogTool
from web_socket.config.database_config.database_config_runner import DatabaseConfigRunner

from functools import wraps
import inspect
from psycopg2 import pool

class PostgresModule:

    def __init__(self):
        self.logger = LogTool.get_logger(self.__class__.__name__)
        
        self.connection_pool = None 
        self.conn = None
        self.cursor = None
        self.fetch_result = None
        
        self.connect_postgres()
        
    def connect_postgres(self):
        
        properties_dict: dict = DatabaseConfigRunner().get_properties()

        # Create a connection pool
        connection_pool = pool.ThreadedConnectionPool(
            1, 30, 
            host=properties_dict.get("database_host"),
            port=properties_dict.get("database_port"),
            user=properties_dict.get("database_id"),  
            password=properties_dict.get("database_password"),  
        )
        self.connection_pool = connection_pool
        return connection_pool

    def set_db(self):
        self.conn = self.connection_pool.getconn()
        self.cursor = self.conn.cursor()
        
        # 연결이상 있으면 끊고 새 연결 가져오기
        try:
            self.conn.ping()  
            
        except Exception:
            self.connection_pool.putconn(self.conn, close=True)
            self.conn = self.connection_pool.getconn()  
            self.cursor = self.conn.cursor()
        
    def reset_db(self):
        
        # 안전한 반환
        if self.conn:
            try:
                self.connection_pool.putconn(self.conn, close=False)  
                
            except Exception:
                pass
            
        self.conn = None
        self.cursor = None
        self.fetch_result = None
        
    def db_query_handler(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            
            try:
                self.set_db()
                result = func(self, *args, **kwargs)
            
            except Exception as e:
                self.logger.info(f"method : {str(func.__name__)}, error : {str(e)}")
                raise
                
            finally:
                self.reset_db()
            
            return result
        return wrapper
    
    def format_read_one(self):
        row_dict = {}
        if self.fetch_result:
            for idx, row in enumerate(self.fetch_result):
                row_dict[self.cursor.description[idx][0]] = row
        return row_dict

    def format_read_all(self):
        row_list = []
        if self.fetch_result:
            for rows in self.fetch_result:
                row_dict = {}
                for idx, row in enumerate(rows):
                    row_dict[self.cursor.description[idx][0]] = row
                row_list.append(row_dict)
        return row_list

    @db_query_handler
    def read_one(self, query, binds=None):
        if binds:
            self.cursor.execute(query, binds)
        else:
            self.cursor.execute(query)
        self.fetch_result = self.cursor.fetchone()
        return self.format_read_one()

    @db_query_handler
    def read_all(self, query, binds=None):
        if binds:
            self.cursor.execute(query, binds)
        else:
            self.cursor.execute(query)
        self.fetch_result = self.cursor.fetchall()
        return self.format_read_all()
    
    @db_query_handler
    def execute_query_with_commit(self, query=None, query_bulk=None, binds=None):
        if not query and not query_bulk:
            self.logger.info(f"{inspect.currentframe().f_code.co_name}, error : no query")
            return

        lastrowids = []

        if query:
            if binds:
                self.cursor.execute(query, binds)
                
            else:
                self.cursor.execute(query)

            if "insert" in query.lower() and "returning" in query.lower():
                lastrowids.append(self.cursor.fetchone()[0])

        elif query_bulk:
            if binds and isinstance(binds, list):
                for q, b in zip(query_bulk, binds):
                    self.cursor.execute(q, b)
                    if "insert" in q.lower()  and "returning" in q.lower():
                        lastrowids.append(self.cursor.fetchone()[0])
            else:
                for q in query_bulk:
                    self.cursor.execute(q)
                    if "insert" in q.lower()  and "returning" in q.lower():
                        lastrowids.append(self.cursor.fetchone()[0])

        self.conn.commit()
        return lastrowids
    
    
    

    # @db_query_handler
    # def execute_query(self, query=None, query_bulk=None):
    #     if not query and not query_bulk:
    #         self.logger.info(f"{inspect.currentframe().f_code.co_name}, error : no query")
    #         return 
        
    #     if query:
    #         self.cursor.execute(query)

    #     elif query_bulk:
    #         for q in query_bulk:
    #             self.cursor.execute(q)

    #     return True