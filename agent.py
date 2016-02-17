import cx_Oracle
import rethinkdb as r
from datetime import datetime

def epoch(dt):
    start_date = datetime.utcfromtimestamp(0)
    return (dt - start_date).total_seconds() * 1000.0

while True:
    ORACLE_USER = "papelex"
    ORACLE_PASSWORD = "FG2hu3DV4T"
    ORACLE_DB = "WINT"

    conn = cx_Oracle.connect(ORACLE_USER, ORACLE_PASSWORD, ORACLE_DB)
    cur = conn.cursor()

    cur.execute('''
        select
            p.NUMITENS,
            p.NUMPED,
            p.DATA,
            p.VLTOTAL,
            p.VLTABELA,
            p.CODPRACA,
            p.POSICAO,
            u.CODUSUR,
            u.NOME,
            s.CODSUPERVISOR,
            s.NOME,
            c.CODCLI,
            c.CLIENTE,
            c.ESTCOM,
            c.MUNICCOM
        from PCPEDC p
        inner join PCUSUARI u
          on u.CODUSUR = p.CODUSUR
        inner join PCSUPERV s
          on s.CODSUPERVISOR = u.CODSUPERVISOR
        inner join PCCLIENT c
          on c.CODCLI = p.CODCLI
        where DATA >= sysdate - 1
    ''')

    header = [row[0] for row in cur.description]
    local = [dict(zip(header, [epoch(el) if isinstance(el, datetime) else el for el in row])) for row in cur]

    cur.close()
    conn.close()

    conn = r.connect('localhost', 28015, db='papelex').repl()
    remote = r.table('orders').group('NUMPED').run(conn) # .filter(r.row['DATA'] >= r.now().date())

    for local_row in local:
        if local_row['NUMPED'] in remote:
            # print(remote[local_row['NUMPED']])
            pass
        else:
            print(local_row)
            r.table('orders').insert(local_row).run(conn)

    conn.close()
