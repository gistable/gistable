import multiprocessing

# split a list into evenly sized chunks
def chunks(l, n):
    return [l[i:i+n] for i in range(0, len(l), n)]


def do_job(job_id, data_slice):
    for item in data_slice:
        print "job", job_id, item


def dispatch_jobs(data, job_number):
    total = len(data)
    chunk_size = total / job_number
    slice = chunks(data, chunk_size)
    jobs = []

    for i, s in enumerate(slice):
        j = multiprocessing.Process(target=do_job, args=(i, s))
        jobs.append(j)
    for j in jobs:
        j.start()


if __name__ == "__main__":
    data = ['a', 'b', 'c', 'd']
    dispatch_jobs(data, 2)

