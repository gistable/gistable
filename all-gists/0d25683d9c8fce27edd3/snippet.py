# airflow/plugins/slack.py

import logging

from airflow.operators.python_operator import PythonOperator
from airflow.plugins_manager import AirflowPlugin
from slackclient import SlackClient
from titan.utils import config


class PythonSlackOperator(PythonOperator):
    def __init__(self, *args, **kwargs):
        super(PythonSlackOperator, self).__init__(*args, **kwargs)

    def _post_slack_message(self, text):
        try:
            sc = SlackClient(config.get('slack', 'token'))
            sc.api_call('chat.postMessage',
                        channel=config.get('slack', 'default_channel'),
                        username='Airflow',
                        icon_url='https://raw.githubusercontent.com/airbnb/airflow/master/airflow/www/static/pin_100.png',
                        text=text)
        except:
            logging.exception('Non-fatal error: could not post message to Slack (text: {text})'.format(**locals()))

    def execute(self, context, *args, **kwargs):
        task_instance = context.get('task_instance')
        dag_run = context.get('dag_run')
        dag = context.get('dag')

        if dag_run is None:
            dag_run_id = 'N/A'
            dag_run_external_trigger = 'N/A'
        else:
            dag_run_id = dag_run.run_id
            dag_run_external_trigger = ':zap:' if dag_run.external_trigger else ':clock3:'

        base_url = config.get('airflow', 'base_url')
        log_url = '{base_url}{task_instance.log_url}'.format(**locals())

        self._post_slack_message(':chicken:{dag_run_external_trigger} Starting task (dag=*{task_instance.dag_id}* task=*{task_instance.task_id}* dagid=*{dag_run_id}*) <{log_url}|logs>'.format(**locals()))
        result = super(PythonSlackOperator, self).execute(context, *args, **kwargs)
        self._post_slack_message(':poultry_leg:{dag_run_external_trigger} Finished task (dag=*{task_instance.dag_id}* task=*{task_instance.task_id}* dagid=*{dag_run_id}*) <{log_url}|logs>'.format(**locals()))


class PythonSlackAPlugin(AirflowPlugin):
    name = 'dp_python_slack'
    operators = [PythonSlackOperator]
    flask_blueprints = []
    hooks = []
    executors = []
    admin_views = []
    menu_links = []
