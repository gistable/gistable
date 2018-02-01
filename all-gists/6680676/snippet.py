# -*- coding: utf-8 -*-

# Copyright © 2013 crodas

# Permission is hereby granted, free of charge, to any
# person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the
# Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the
# Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice
# shall be included in all copies or substantial portions of
# the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
# OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from disco.job import Job
from disco.core import result_iterator
from disco.worker.classic.worker import Params
from disco.util import kvgroup
from disco.worker.task_io import chain_reader
import sys

separator = "<separator>"

def partition_function(key, nr_partitions, params):
    k = ZKEY(key)
    return hash(k[0]) % nr_partitions

def mapReduce(zclass):
    zclass.partition  = staticmethod(partition_function)
    zclass.map_reader = staticmethod(chain_reader)
    zclass.sort       = True
    zclass.merge_partitions = True
    zclass.partitions = 6
    return zclass

def run(task, zinput, payload=None):
    import pagerank

    zclass = getattr(pagerank, task)
    job = zclass();
    job.params     = Params(payload=payload)

    job.run(input=zinput)
    result = job.wait(show = False)

    return result

def ZKEY(args):
    global separator
    return args.split(separator)

def KEY(*args):
    global separator
    _args = []
    for val in args:
        if (type(val) == int or type(val) == float):
            val = str(val)
            if len(val) < 10:
                val = val.rjust(10, '0')
        _args.append(str(val))
    return separator.join(_args)

"""
Count backlinks that each nodes had
"""
@mapReduce
class Prepare(Job):

    @staticmethod
    def map(line, params):
        parts = line.split()

        # Calculate the outlinks for each node
        yield parts[0], 1

    @staticmethod
    def reduce(iter, params):
        lastId = None
        for id, value in iter:
            if lastId == None:
                lastId = id
                sum    = 0
            if lastId != id:
                yield lastId, {"outlink":sum, "pagerank": 0.15, "id": lastId}
                lastId = id
                sum    = 0
            sum = sum + value

        yield lastId, {"outlink":sum, "pagerank": 0.15, "id": lastId}
            
"""
Create and update the Graph in a computation friendly format
"""
@mapReduce
class UpdateGraph(Job):

    @staticmethod
    def map(line, params):
        if type(line) == str:
            parts = line.split()
        else:
            parts = line

        key   = parts[0]
        value = parts[1]

        if type(line) == str:
            yield KEY(key, 3), value
        elif type(value) == float:
            yield KEY(key, 2), value
        else:
            yield KEY(key, 1), value

    @staticmethod
    def reduce(iter, params):
        lastId = None
        node   = None
        for id, data in iter:
            zid = ZKEY(id)
            if lastId == None or zid[0] != lastId:
                lastId = zid[0]
                node = data
            elif int(zid[1]) == 2:
                node['pagerank'] = data
            elif int(zid[1]) == 3:
                yield data, node


"""
Calculate the PageRank
"""
@mapReduce
class PageRank(Job):

    @staticmethod
    def map(line, params):
        key = line[0]
        value = line[1]
        yield key, value['pagerank']/value['outlink']

    @staticmethod
    def reduce(iter, params):
        lastId = None
        sum    = 0
        for id, value in iter:
            if lastId == None:
                lastId = id
            elif lastId != id:
                yield lastId, 0.15 + 0.85 * sum
                lastId = id
                sum    = 0
            sum = sum + value

        if sum > 0:
            yield lastId, 0.15 + 0.85 * sum

"""
Sort each output by their pagerank (in descendent order)
"""
@mapReduce
class Sort(Job):

    @staticmethod
    def map(line, params):
        key = line[0]
        value = line[1]
        yield str(int((1/value)*1000000000)).rjust(20, '0'), [key, value]

    @staticmethod
    def reduce(iter, params):
        for key,value in iter:
            yield value[0], value[1]

if __name__ == "__main__":
    input = 'pagerank'
    nodes = run('Prepare', [input])

    for i in range(5):
        if i > 0:
            graph = run("UpdateGraph", [input, nodes, pagerank])
        else:
            graph = run("UpdateGraph", [input, nodes])
    
        pagerank = run("PageRank", graph)


    f = open('salida.txt', 'w')
    for word, value in result_iterator(run('Sort', [pagerank])):
        f.write("%s\t\t%s\n" %(word,value))
    f.close()
