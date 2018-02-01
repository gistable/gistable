import numpy as np
import multiprocessing as multi

def chunks(n, page_list):
    """Splits the list into n chunks"""
    return np.array_split(page_list,n)
 
cpus = multi.cpu_count()
workers = []
page_list = ['www.website.com/page1.html', 'www.website.com/page2.html'
            'www.website.com/page3.html', 'www.website.com/page4.html']

page_bins = chunks(cpus, page_list)

for cpu in range(cpus):
    sys.stdout.write("CPU " + str(cpu) + "\n")
    #Process that will send corresponding list of pages 
    #to the function perform_extraction
    worker = multi.Process(name=str(cpu), 
                           target=perform_extraction, 
                           args=(page_bins[cpu],))
    worker.start()
    workers.append(worker)

for worker in workers:
    worker.join()
    
def perform_extraction(page_ranges):
    """Extracts data, does preprocessing, writes the data"""
    #do requests and BeautifulSoup
    #preprocess the data
    file_name = multi.current_process().name+'.txt'
    #write into current process file