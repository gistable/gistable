import os
import unittest

from airflow.models import DagBag

class TestDags(unittest.TestCase):
    """
    Generic tests that all DAGs in the repository should be able to pass.
    """

    VALID_DAG_OWNERS = set([
        'team1',
        'team2',
        'team3',
    ])

    VALID_DAG_EMAILS = set([
        'team1-alerts@foo.com',
        'team2-alerts@foo.com',
        'team3-alerts@foo.com',
    ])

    def _get_dagbag(self):
        dag_folder = os.getenv('AIRFLOW_DAGS', False)
        self.assertTrue(
            dag_folder,
            'AIRFLOW_DAGS must be set to a folder that has DAGs in it.')
        return DagBag(dag_folder=dag_folder, include_examples=False)

    def test_dagbag_import(self):
        """
        Verify that Airflow will be able to import all DAGs in the repository.
        """
        dagbag = self._get_dagbag()
        self.assertFalse(
            len(dagbag.import_errors),
            'There should be no DAG failures. Got: {}'.format(dagbag.import_errors))

    def test_dagbag_emails(self):
        """
        Check that every DAG has a known email in the email list, and a valid
        owner, so we know which team owns which DAG.
        """
        dagbag = self._get_dagbag()
        for dag_id, dag in dagbag.dags.items():
            tasks_with_email_cnt = 0
            for task in dag.tasks:
                self._check_owner(task.owner, dag_id, task.task_id)
                if task.email:
                    self._check_email(task.email, dag_id, task.task_id)
                    tasks_with_email_cnt += 1

            if 'owner' in dag.default_args:
                self._check_owner(dag.default_args.get('owner', False), dag_id)
            if 'email' in dag.default_args:
                self._check_email(dag.default_args.get('email', False), dag_id)

            self.assertTrue(tasks_with_email_cnt == len(dag.tasks) or dag.default_args.get('email', False), \
                'Either all tasks or default_args must have email set: {}'.format(dag_id))

    def _check_owner(self, owner, dag_id, task_id=False):
        # Check owner against valid owner list.
        error_msg = 'DAG must have a valid owner ({}) defined: dag_id={}, task_id={}' \
            .format(self.VALID_DAG_OWNERS, dag_id, task_id)
        self.assertTrue(owner in self.VALID_DAG_OWNERS, error_msg)

    def _check_email(self, email, dag_id, task_id=False):
        # Airflow allows both a single email, as well as a list.
        emails = email if isinstance(email, list) else [email]
        error_msg = 'DAG must have a valid email ({}) defined: dag_id={}, task_id={}' \
            .format(self.VALID_DAG_EMAILS, dag_id, task_id)
        self.assertEqual(len(self.VALID_DAG_EMAILS.intersection(emails)), len(emails), error_msg)
