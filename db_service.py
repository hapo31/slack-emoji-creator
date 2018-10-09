import psycopg2


class PostgresService:
    def __init__(self, host, db_name, user, password):
        self._connection = psycopg2.connect(
            host=host, database=db_name, user=user, password=password)

    def update_login_session(self, name, cookie):
        with self._connection.cursor() as cur:
            cur.execute(
                "update session set session = %s where name = %s", (
                    name, cookie)
            )
            self._connection.commit()
            return cur.rowcount == 1

    def get_login_session(self, name):
        with self._connection.cursor() as cur:
            cur.execute(
                "select session from login_session where name = %s", (name,))
            (session) = cur.fetchone()
            if len(session) > 0:
                return session[0].strip()
            else:
                return ""

    def close(self):
        self._connection.close()


if __name__ == '__main__':
    service = PostgresService(
        "", "", "", "")
