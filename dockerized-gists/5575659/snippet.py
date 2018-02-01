from random import randint
from myhdl import *

class MemPort:
    def __init__(self,depth=128):
        self.addr = Signal(modbv(0, min=0, max=depth))
        self.wdata = Signal(intbv(0)[8:])
        self.we = Signal(bool(0))
        self.rdata = Signal(intbv(0)[8:])
    def get_signals(self):
        return self.addr,self.wdata,self.we,self.rdata

def m_dual_port_ram(clock,porta,portb,depth=128):
    mem = [Signal(intbv(0)[8:]) for ii in range(depth)]
    
    def mem_logic(clock,wdata,addr,we,rdata,mem):
        @always(clock.posedge)
        def hdl():
            if we:
                mem[addr].next = wdata
            rdata.next = mem[addr]
        return hdl

    mem_ports = []
    for port in (porta,portb):
        mem_ports.append(mem_logic(clock,port.wdata,port.addr,
                                   port.we,port.rdata,mem))
        
    return mem_ports

def m_spi(clock,reset,sck,mosi,miso,csn,port):
    addr,wdata,we,rdata = port.get_signals()    
    # silly logic, non-sensical
    @always_seq(clock.posedge,reset=reset)
    def hdl():
        if csn:
            we.next = True
            wdata.next = rdata
        else:
            we.next = False
        mosi.next = rdata[0]
    return hdl

def m_sns(clock,reset,port,ext_data,ext_dv):
    addr,wdata,we,rdata = port.get_signals()
    @always_seq(clock.posedge,reset=reset)
    def hdl():
        if ext_dv:
            we.next = True
            wdata.next = ext_data
            addr.next = addr+1
        else:
            we.next = False
    return hdl

def m_spi_mem(clock,reset,sck,mosi,miso,csn,ext_data,ext_dv):
    porta = MemPort()
    portb = MemPort()
    g_spi = m_spi(clock,reset,sck,mosi,miso,csn,porta)
    g_sns = m_sns(clock,reset,portb,ext_data,ext_dv)
    g_dpr = m_dual_port_ram(clock,porta,portb)
    
    return g_spi,g_sns,g_dpr

def convert():
    clock = Signal(bool(0))
    reset = ResetSignal(0,active=0,async=True)
    sck,mosi,miso,csn = [Signal(bool(0)) for ii in range(4)]
    ext_data = Signal(intbv(0)[8:])
    ext_dv = Signal(bool(0))
    toVerilog(m_spi_mem,clock,reset,sck,mosi,miso,csn,ext_data,ext_dv)
    toVHDL(m_spi_mem,clock,reset,sck,mosi,miso,csn,ext_data,ext_dv)


def test():
    clock = Signal(bool(0))
    reset = ResetSignal(0,active=0,async=True)
    sck,mosi,miso,csn = [Signal(bool(0)) for ii in range(4)]
    ext_data = Signal(intbv(0)[8:])
    ext_dv = Signal(bool(0))

    tb_dut = traceSignals(m_spi_mem,clock,reset,sck,mosi,miso,csn,
                          ext_data,ext_dv)

    @always(delay(3))
    def tb_clock_gen():
        clock.next = not clock

    @instance
    def tb_stim():
        reset.next = False
        yield delay(10)
        reset.next = True
        yield delay(10)
        yield clock.posedge

        for ii in range(13):
            ext_data.next = randint(0,255)
            ext_dv.next = True
            yield clock.posedge
            ext_dv.next = False
            yield delay(133)
            yield clock.posedge

        raise StopSimulation

    Simulation((tb_dut,tb_clock_gen,tb_stim)).run()

if __name__ == '__main__':
    test()
    convert()
