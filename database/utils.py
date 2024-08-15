import datetime as datetime

from sqlalchemy import text
from sqlalchemy.sql import expression
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.types import DateTime

class utcnow(expression.FunctionElement):
    type = DateTime()
    inherit_cache = True

@compiles(utcnow, 'postgresql')
def pg_utcnow(element, compiler, **kw):
    '''
    A function that works like “CURRENT_TIMESTAMP” except applies the appropriate conversions so that the time is in UTC time.
    Source: https://docs.sqlalchemy.org/en/20/core/compiler.html#utc-timestamp-function
    '''
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"

def update_sql_id_sequence(engine, table_name):
    '''
    This function execute SQL comments to reset PostgreSQL id sequence
    Source:  https://stackoverflow.com/questions/244243/how-to-reset-postgres-primary-key-sequence-when-it-falls-out-of-sync
    '''
    statement = text("""BEGIN;
                LOCK TABLE text_embeddings IN EXCLUSIVE MODE;
                SELECT setval('text_embeddings_id_seq', COALESCE((SELECT MAX(id)+1 FROM text_embeddings),1),FALSE); 
                COMMIT;"""
                )

    with engine.connect() as con:
        con.execute(statement)


def table_exists(engine, name):
    """ 
    Check if table exist. Source:  https://stackoverflow.com/questions/64861610/easily-check-if-table-exists-with-python-sqlalchemy-on-an-sql-database
    """
    ins = sqlalchemy.inspect(engine)
    ret =ins.dialect.has_table(engine.connect(),name)
    print('Table "{}" exists: {}'.format(name, ret))
    return ret

