import psycopg2

conn = psycopg2.connect(database="DB_NAME",
                        host="DB_HOST",
                        user="DB_USER",
                        password="DB_PASSWORD",
                        port="5432")