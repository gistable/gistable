# -*- coding: utf-8 -*-
from airflow.operators.http_operator import SimpleHttpOperator
from airflow.operators.postgres_operator import PostgresOperator
from airflow.operators.subdag_operator import SubDagOperator
from airflow.operators.sensors import SqlSensor
from airflow.hooks.postgres_hook import PostgresHook

from airflow.operators.python_operator import PythonOperator

from airflow.models import Variable, DAG

from datetime import datetime, timedelta

default_args = {
    'owner': '@tmarthal',
    'start_date': datetime(2017, 2, 1),
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


##
## The DAG for the application audience job to run
##
dag = DAG('sensor_dag_creation_inoperator',
    default_args=default_args,
    schedule_interval = '*/5 * * * *' # every five minutes
)

dag.doc = """
Simple http call which triggers when a row shows up in a database
"""

def response_check(response):
    """
    Dumps the http response and returns True when the http call status is 200/success
    """
    print("checking the reponse from the app")
    print(response.content)
    return response.status_code == 200


def process_new_accounts(ds, **kwargs):
    """
    The sensor has detected new ids to process, so we call the http operator for each
    """

    select_sql = "SELECT id from audiences where created_at > '{ds}'".format(ds=ds)
    print("running select sql {}".format(select_sql))

    pg_hook = PostgresHook(postgres_conn_id='letterpress-app')
    connection = pg_hook.get_conn()

    cursor = connection.cursor()
    cursor.execute(select_sql)

    account_ids = cursor.fetchall()

    for account_id in account_ids:
        # Create a sub-dag with each new id
        # the child dag name
        export_account_task_name = 'task_process_account_%s' % account_id

        print("starting task: {}".format(export_account_task_name))
        export_account_dag = DAG(
            dag_id=export_account_task_name,
            default_args=default_args,
            schedule_interval='*/5 * * * *'  # '@once'
        )

        ## This hits the account export url, _endpoint/account/export?id={ACCOUNT_ID}&token={AUTH_TOKEN}
        account_export_endpoint_task = SimpleHttpOperator(
            task_id='account_export_endpoint_task_%s' % (account_id),
            http_conn_id='application',
            method='GET',
            endpoint='_endpoint/account/export',
            data={"id": "{}".format(account_id), "token": Variable.get("APPLICATION_ACCESS_TOKEN")},  # http params
            response_check=response_check,  # will retry based on default_args if it fails
            dag=export_account_dag)

        print("Created account processing DAG {}".format(export_account_dag.dag_id))

        # register the dynamically created DAG in the global namespace?
        globals()[export_account_task_name] = export_account_dag


    return account_ids



sensor = SqlSensor(
    task_id='account_creation_check',
    conn_id='account-database',
    poke_interval=600, #do the select every 600 seconds, 5 minutes
    sql="SELECT id from accounts where created_at > '{{ds}}' LIMIT 1",
    dag=dag
)

process_new_accounts_task = PythonOperator(task_id='process_new_accounts',
                   provide_context=True,
                   python_callable=process_new_accounts,
                   dag=dag)


sensor >> process_new_accounts_task
