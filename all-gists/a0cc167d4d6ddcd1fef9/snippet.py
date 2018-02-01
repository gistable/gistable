MAP_SLACK_ATTACHMENTS = [
    {
        "fallback": "{{params.map}} {{ task_instance.xcom_pull(task_ids=params.map, key='slack_status') }}",
        "pretext": "{{params.map}} update {{ task_instance.xcom_pull(task_ids=params.map, key='slack_status') }}",
        "fields": [
            {
                "title": "Copied",
                "value": "{{ task_instance.xcom_pull(task_ids=params.map, key='copied') }}",
                "short": True
            }
          ]
    }
  ]
  
MAP_EMAIL_CONTENT = """
<b>Map:</b> {{ params.map }}<br>
<b>Date:</b> {{ ds }}<br>
<p>
<b>Copied:</b> {{ task_instance.xcom_pull(task_ids=params.map, key='copied') }}<br>
"""

def update_hdfs(ds, **kwargs):
    ....
    kwargs['ti'].xcom_push(key='slack_status', value='danger')
    if success:
        kwargs['ti'].xcom_push(key='slack_status', value='good')
        kwargs['ti'].xcom_push(key='copied', value=int(m.group(1)))

speedmap = PythonOperator(
    task_id='speedmap',
    python_callable=update_hdfs,
    params={'map': 'speedmap'},
    provide_context=True,
    pool = 'speedmap',  # no simultaneous runs
    dag=dag)

map_slack = SlackAPIPostOperator(
        task_id='speedmap_slack',
        channel="#airflow-test",
        token=Variable.get('slack_token'),
        params={'map': speedmap},
        text='',
        attachments=MAP_SLACK_ATTACHMENTS,
        trigger_rule='all_done',
        dag=dag)
dag.set_dependency('speedmap', 'speedmap_slack')

map_email = EmailOperator(
        task_id='speedmap_email',
        to="adrian@opensignal.com",
        params={'map': map},
        subject=map  + " {{ ds }} {{ task_instance.xcom_pull(task_ids=params.map, key='slack_status') }}",
        html_content=MAP_EMAIL_CONTENT,
        trigger_rule='all_done',
        dag=dag)
# Just to show an alternative approach
map_email.set_upstream(speedmap)