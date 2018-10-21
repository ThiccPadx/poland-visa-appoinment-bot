# -*- coding: utf-8 -*-
try:
    import logging
    import pymssql

except ImportError as e:
    print e
    logging.error(str(e))
    sys.exit(1)


__file__ = 'mssqlPipe'
logger = logging.getLogger(__file__)
# type: mssql
# server: smartitcorp.database.secure.windows.net
# database: iVisa
# username: gb
# password: 7=^{YwjrS!r3mXu.5sOM4wc,MSOzDMZO2EZ"3${342,A2lMytq


class Conn(object):

    def __init__(self, srvr, usr, pss, db):

        self.srvr = srvr
        self.usr = usr
        self.pss = pss
        self.db = db

        pass
    # get connection pipe instance

    def connect(self):
        try:
            self.conn = pymssql.connect(server=self.srvr,
                                        user=self.usr, password=self.pss, database=self.db, port=1433)
            self.cursor = self.conn.cursor()
        except pymssql.Error as e:
            print str(e)
            logging.error(
                'Could not connect to azure database. Reason: {0}'.format(str(e)))
        pass

    def getConn(self):
        return self.conn

    def close(self):
        self.cursor.close()
        self.conn.close()
        pass

    def executeQuery(self, query):
        self.cursor.execute(query)
        row = self.cursor.fetchone()

        # for i in res:
        #    print i
        return row[0]

    def insert(self, query):
        pass

    def update(self, query):
        pass

    def delete(self, query):
        pass
    pass
