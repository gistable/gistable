from myhdl import *

def switchchannels(mem2d, q, clk):

    def assign_los(mem1d_a, mem1d_b):
        print(mem1d_a, mem1d_b)
        for i in range(len(mem1d_a)):
            mem1d_a[i].next = mem1d_b[i]
        return mem1d_a

    @always(clk.posedge)
    def switch():
        print('switch')
        print(mem2d)
        mem2d[1] = assign_los(mem2d[1], mem2d[0])

    @always(clk.posedge)
    def logic():
        print('logic')
        print(q, mem2d)
        mem2d[0][0].next = mem2d[0][1]
        mem2d[0][1].next = q
        
    return switch, logic
        
from random import randrange

def test_switchchannels():
    
    clk = Signal(bool(0))
    q = Signal(intbv(0)[4:])
    mem2d = [[Signal(intbv(0)[4:]), Signal(intbv(0)[4:])] , [Signal(intbv(1)[4:]), Signal(intbv(1)[4:])]]

    print('init')
    print(q)
    print(clk)
    print(mem2d)

    switch_inst = switchchannels(mem2d, q, clk)
    
    @always(delay(10))
    def clkgen():
        clk.next = not clk

    @always(clk.negedge)
    def stimulus():
        print('neg')
        print(mem2d)
        q.next = randrange(2)

    return switch_inst, clkgen, stimulus

def simulate(timesteps):
    traceSignals.timescale = "1ps"
    tb = traceSignals(test_switchchannels)
    sim = Simulation(tb)
    sim.run(timesteps)

simulate(80)

