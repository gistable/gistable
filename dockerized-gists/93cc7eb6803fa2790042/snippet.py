import luigi
import time

class TimeTaskMixin(object):
    '''
    A mixin that when added to a luigi task, will print out
    the tasks execution time to standard out, when the task is
    finished
    '''
    @luigi.Task.event_handler(luigi.Event.PROCESSING_TIME)
    def print_execution_time(self, processing_time):
        print('### PROCESSING TIME ###: ' + str(processing_time))


class TaskA(luigi.ExternalTask, TimeTaskMixin):
    '''
    A simple task representing a simple file with a few rows
    of dummy content
    '''
    def output(self):
        return luigi.LocalTarget('input.txt')
    

class TaskB(luigi.Task, TimeTaskMixin):
    '''
    A simple task that just outputs the content of its dependency
    into a new file with the the same name plus the extension .taskb
    '''
    def requires(self):
        return TaskA()

    def output(self):
        return luigi.LocalTarget(self.input().path + '.taskb')

    def run(self):
        time.sleep(1)
        with self.input().open() as infile, self.output().open('w') as outfile:
            for row in infile:
                outfile.write(row)


class TaskC(luigi.Task, TimeTaskMixin):
    '''
    A simple task that just outputs the content of its dependency
    into a new file with the the same name plus the extension .taskc
    '''
    def requires(self):
        return TaskB()

    def output(self):
        return luigi.LocalTarget(self.input().path + '.taskc')

    def run(self):
        time.sleep(2)
        with self.input().open() as infile, self.output().open('w') as outfile:
            for row in infile:
                outfile.write(row)


# If this file is executed as a script, run the last class in the dependency
# graph, TaskC.
if __name__ == '__main__':
    luigi.run(main_task_cls=TaskC)
