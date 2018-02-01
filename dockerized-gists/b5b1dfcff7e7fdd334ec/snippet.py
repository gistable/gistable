import multiprocessing
import sys

THREADS = 3

# Used to prevent multiple threads from mixing thier output
GLOBALLOCK = multiprocessing.Lock()


def func_worker(args):
    """This function will be called by each thread.
    This function can not be a class method.
    """
    # Expand list of args into named args.
    str1, str2 = args
    del args

    # Work
    # ...

    # Print output
    GLOBALLOCK.acquire()
    print(str1)
    GLOBALLOCK.release()

    # Print other output (possibly intermixed)
    GLOBALLOCK.acquire()
    print(str2)
    GLOBALLOCK.release()


def main(argp=None):
    """Multiprocessing Spawned Example
    """
    # Create the number of threads you want
    pool = multiprocessing.Pool(THREADS)

    # Define two jobs, each with two args.
    func_args = [
        ('Hello', 'World',), 
        ('Goodbye', 'World',), 
    ]


    try:
        # Spawn up to 9999999 jobs, I think this is the maximum possible.
        # I do not know what happens if you exceed this.
        pool.map_async(func_worker, func_args).get(9999999)
    except KeyboardInterrupt:
        # Allow ^C to interrupt from any thread.
        sys.stdout.write('\033[0m')
        sys.stdout.write('User Interupt\n')
    pool.close()

if __name__ == '__main__':
    main()
