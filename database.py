import psycopg2
class DB:
    def __init__(self, DATABASE_URL):
        self.DATABASE_URL = DATABASE_URL;
        self.connection = psycopg2.connect(DATABASE_URL, sslmode='require')
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()

    def execute(self, sql):
        self.cursor.execute(sql)
        return self.cursor.fetchall()
