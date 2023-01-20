import sys
import os
import multiprocessing
import subprocess

def work(staname):
    print 'Processing station:',staname
    print 'Parent process:', os.getppid()
    print 'Process id:', os.getpid()
   # cmd = [ "/bin/bash" "/path/to/executable/create_graphs.sh","--name=%s" % (staname) ]
   # return subprocess.call(cmd, shell=False)

if __name__ == '__main__':

    my_list = [ 'XYZ', 'ABC', 'NYU' ]

    my_list.sort()

    print my_list

    # Get the number of processors available
    num_processes = multiprocessing.cpu_count()
    print "number of processes running at the cpu is %d" % num_processes

    threads = []

    len_stas = len(my_list)

    print "+++ Number of stations to process: %s" % (len_stas)

    # run until all the threads are done, and there is no data left

    for list_item in my_list:

        # if we aren't using all the processors AND there is still data left to
        # compute, then spawn another thread

        if( len(threads) < num_processes ):

            p = multiprocessing.Process(target=work,args=[list_item])

            p.start()

            print p, p.is_alive()

            threads.append(p)

        else:

            for thread in threads:

                if not thread.is_alive():

                    threads.remove(thread)