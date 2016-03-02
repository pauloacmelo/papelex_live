import cx_Oracle
import rethinkdb as r
from datetime import datetime
from time import sleep
import traceback
import sys
import os

CLIENT_NAME = 'papelex'
ORACLE_USER = "papelex"
ORACLE_PASSWORD = "FG2hu3DV4T"
ORACLE_DB = "WINT"

def epoch(dt):
    start_date = datetime.utcfromtimestamp(0)
    return (dt - start_date).total_seconds() * 1000.0

def keymap(value, key):
    if hasattr(key, '__iter__') and not isinstance(key, str):
        return tuple([value[k] for k in key])
    return value[key]

SYNCS = [
    {'query': '''
        select
            p.NUMITENS,
            p.NUMPED,
            to_char(p.DATA, 'YYYY-MM-DD') DATA,
            p.VLTOTAL,
            p.VLTABELA,
            p.CODPRACA,
            p.POSICAO,
            u.CODUSUR,
            u.NOME NOME_RCA,
            s.CODSUPERVISOR,
            s.NOME NOME_SUPERVISOR,
            c.CODCLI,
            c.CLIENTE,
            c.ESTCOM,
            c.MUNICCOM,
            (
              select 
                '{' || LISTAGG('"' || PCDEPTO.DESCRICAO || '": ' || sum(QT), ',') WITHIN GROUP (ORDER BY PCDEPTO.DESCRICAO) || '}'
              from PCPEDI, PCPRODUT, PCDEPTO
              where 1=1
                and PCPRODUT.CODEPTO = PCDEPTO.CODEPTO
                and PCPRODUT.CODPROD = PCPEDI.CODPROD
                and NUMPED = p.NUMPED
              group by PCDEPTO.DESCRICAO
            ) MIX
        from PCPEDC p
        inner join PCUSUARI u
          on u.CODUSUR = p.CODUSUR
        inner join PCSUPERV s
          on s.CODSUPERVISOR = u.CODSUPERVISOR
        inner join PCCLIENT c
          on c.CODCLI = p.CODCLI
        where DATA >= sysdate - 10
          and p.DTCANCEL is null
          and c.CODCLI not in (1, 71291, 4, 98006, 53931, 100303)
          and p.CONDVENDA not in (10, 8)''',
    'table': 'orders',
    'key': 'NUMPED'},
    {'query': '''
        select
            CODSUPERVISOR,
            sum(PCMETARCA.VLVENDAPREV) VALOR_META,
            to_char(sysdate, 'YYYY-MM-DD') DATA
        from PCMETARCA
        inner join PCUSUARI
            on PCUSUARI.CODUSUR = PCMETARCA.CODUSUR
        where 1=1
            and trunc(DATA) = trunc(sysdate)\
        group by CODSUPERVISOR''',
    'table': 'goal',
    'key': ('CODSUPERVISOR', 'DATA')},
    {'query': '''
        select SYSDATE CREATED_AT, PCORCAVENDAC.NUMORCA, PCPRODUT.CODEPTO, PCORCAVENDAC.NUMREGIAO, PCORCAVENDAC.DATA, PCORCAVENDAC.VLTOTAL, PCORCAVENDAC.CODCLI, PCORCAVENDAC.CODUSUR, PCORCAVENDAC.VLTABELA, PCORCAVENDAC.CODFILIAL, PCORCAVENDAC.VLDESCONTO, PCORCAVENDAC.TIPOVENDA, PCORCAVENDAC.NUMITENS, PCORCAVENDAC.CODEMITENTE, PCORCAVENDAC.DTCANCEL, PCORCAVENDAC.POSICAO, PCORCAVENDAI.CODPROD, PCORCAVENDAI.CODST, PCORCAVENDAI.NUMITEMORCA, PCORCAVENDAI.NUMSEQ, PCORCAVENDAI.ORCAVENDAAUTORIZADO, PCORCAVENDAI.PERCDESC_POLITICA, PCORCAVENDAI.PERCDESCQUANT, PCORCAVENDAI.PERDESC, PCORCAVENDAI.PERDESCAUX, PCORCAVENDAI.PERDESCAVISTA, PCORCAVENDAI.PERDESCCOM, PCORCAVENDAI.PERDESCCUSTO, PCORCAVENDAI.PERDESCFIN, PCORCAVENDAI.PERDESCFLEX, PCORCAVENDAI.PERDESCISENTOICMS, PCORCAVENDAI.PERDESCNEGOCIADO, PCORCAVENDAI.PERDESCPAUTA, PCORCAVENDAI.PERDESCPOLITICA, PCORCAVENDAI.PERDESCTAB, PCORCAVENDAI.PORIGINAL, PCORCAVENDAI.PTABELA, PCORCAVENDAI.PVENDA, PCORCAVENDAI.PVENDA1, PCORCAVENDAI.QT, PCORCAVENDAI.ST, PCORCAVENDAI.VLDESCCOM, PCORCAVENDAI.VLDESCCUSTOCMV, PCORCAVENDAI.VLDESCFIN, PCORCAVENDAI.VLDESCFLEX, PCORCAVENDAI.VLDESCICMISENCAO, PCORCAVENDAI.VLDESCPISSUFRAMA, PCORCAVENDAI.VLDESCRODAPE, PCORCAVENDAI.VLDESCSUFRAMA
        from PCORCAVENDAC, PCORCAVENDAI, PCPRODUT
        where 1=1
            and PCORCAVENDAI.NUMORCA = PCORCAVENDAC.NUMORCA
            and PCORCAVENDAI.CODPROD =  PCPRODUT.CODPROD
            and PCORCAVENDAC.POSICAO = 'B'
        ''',
    'table': 'discount_authorization',
    'key': ('NUMORCA', 'CODPROD')},    
]

while True:
    try:
        os.environ['NLS_LANG'] = 'AMERICAN_AMERICA.UTF8'
        ora_conn = cx_Oracle.connect(ORACLE_USER, ORACLE_PASSWORD, ORACLE_DB)
        cur = ora_conn.cursor()
        for sync in SYNCS:
            # Builds local dict (values on client's database)
            cur.execute(sync['query'])
            header = [row[0] for row in cur.description]
            local = [dict(zip(header, [epoch(el) if isinstance(el, datetime) else el for el in row])) for row in cur]
            # Builds remote dict (values BI's database)
            conn = r.connect('localhost', 28015, db=CLIENT_NAME).repl()
            if hasattr(sync['key'], '__iter__') and not isinstance(sync['key'], str):
                remote = r.table(sync['table']).group(*sync['key']).run(conn) # .filter(r.row['DATA'] >= r.now().date())
            else:
                remote = r.table(sync['table']).group(sync['key']).run(conn) # .filter(r.row['DATA'] >= r.now().date())

            for local_row in local:
                if keymap(local_row, sync['key']) in remote:
                    # print(remote[local_row['NUMPED']])
                    pass
                else:
                    print(local_row)
                    r.table(sync['table']).insert(local_row).run(conn)
            conn.close()
    except Exception as e:
        print(e)
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        traceback.print_tb(exceptionTraceback, limit=1, file=sys.stdout)
    finally:
        cur.close()
        ora_conn.close()        
    sleep(5)
