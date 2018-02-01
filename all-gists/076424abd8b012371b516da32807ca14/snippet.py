"""
Code that goes along with the Airflow tutorial located at:
https://github.com/airbnb/airflow/blob/master/airflow/example_dags/tutorial.py
"""
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.generic_transfer import GenericTransfer
from airflow.contrib.hooks import FTPHook
from airflow.hooks.mysql_hook import MySqlHook

from datetime import datetime, timedelta
import codecs
import os
import logging
five_days_ago = datetime.combine(datetime.today() - timedelta(5), datetime.min.time())
default_args = {
    'owner': 'flolas',
    'depends_on_past': True,
    'start_date': five_days_ago,
    'email': ['felipe.lolas013@bci.cl'],
    'email_on_failure': False,
    'email_on_retry': False,
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    #'end_date': datetime(2016, 1, 1),
    }
"""
This function get a file from an FTP, then save it to a folder on worker fs
TODO: Delete blank file when file not found, then skip
"""
def download_file_from_ftp(remote_path, local_path, prefix, suffix,conn_id, ext, **kwargs):
    conn = FTPHook(ftp_conn_id=conn_id)
    date = str(kwargs['execution_date'].day) + '-' + str(kwargs['execution_date'].month) + '-' + str(kwargs['execution_date'].year) 
    fl = prefix + date + suffix + '.' + ext
    remote_filepath = remote_path + fl
    local_filepath = local_path + fl
    logging.info('Getting file: {}'.format(remote_filepath))
    conn.retrieve_file(remote_filepath, local_filepath)
    return local_filepath
"""
Expand columns process with pandas and save to the same csv
"""
def process_file_from_fs(header=None, sep=',', decimal='.', **kwargs):
    import pandas as pd
    def unpack_col(col_to_unpack, df_to_append = None, header = 'col', sep=',', na_value=''):
        unpacked_cols = col_to_unpack.fillna(na_value).apply(lambda x: pd.Series(x.split(','))).fillna(na_value)
        #add dynamic columns names based on # of rows and parameter header passed for prefix (header_#)
        col_names = []
        for i in unpacked_cols.columns:
            col_names.append(header + '_' + str(i))
        unpacked_cols.columns = col_names
        if isinstance(df_to_append, pd.DataFrame):
            #return df concatenated with previously unpacked columns
            return pd.concat([df_to_append, unpacked_cols], axis=1)
        else:
            #return df only with unpacked columns
            return unpacked_cols
    # Esto lo que hace es recibir el output de la tarea anterior con xcom(local_filepath si se logro descargar el archivo)
    local_filepath = kwargs['ti'].xcom_pull(task_ids='download_file')
    df = pd.read_csv(local_filepath, sep = sep, header = header, decimal = '.', parse_dates=True, encoding='utf-8')
    df = unpack_col(df[1], df, header='sent_mail')
    df = unpack_col(df[2], df, header='recv_mail')
    df.to_csv(local_filepath, sep='\t', encoding='utf-8')
    return local_filepath

def bulk_load_sql(table_name, **kwargs):
    local_filepath = kwargs['ti'].xcom_pull(task_ids='download_file')
    conn = MySqlHook(conn_name_attr='ib_sql')
    conn.bulk_load(table_name, local_filepath)
    return table_name
dag = DAG('carga-mails-ejecutivos-6', default_args=default_args,schedule_interval="@daily")
t1 = PythonOperator(
        task_id='download_file',
        python_callable=download_file_from_ftp,
        provide_context=True,
        op_kwargs={'remote_path': '/home/flolas/files/'
                    ,'local_path': '/usr/local/airflow/files/'
                    ,'ext': 'csv'
                    ,'prefix': 'mail_'
                    ,'suffix': ''
                    ,'conn_id': 'ftp_servidor'
                  },
        dag=dag)
t2 = PythonOperator(
        task_id='process_file',
        python_callable=process_file_from_fs,
        provide_context=True,
        op_kwargs={'sep': '|'},
        dag=dag)
t3 = PythonOperator(
        task_id='file_to_MySql',
        provide_context=True,
        python_callable=bulk_load_sql,
        op_kwargs={'table_name': 'MailsEjecutivos'},
        dag=dag)
t1 >> t2
t2 >> t3
