import psycopg2


class PostgreConnector():
    def __init__(self, db_host, db_port, db_name, db_user, db_password):

        self.db_host = db_host
        self.db_port = db_port
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self.conn = None
    
    def connect(self):
        conn = psycopg2.connect(
            host=self.db_host,
            port=self.db_port,
            dbname=self.db_name,
            user=self.db_user,
            password=self.db_password
        )
        self.conn = conn

    def execute(self, query):
        cursor = self.conn.cursor()
        cursor.execute(query)
        self.conn.commit()
        # 获取该次事务的执行状态
        status = cursor.statusmessage
        cursor.close()
        return status
    