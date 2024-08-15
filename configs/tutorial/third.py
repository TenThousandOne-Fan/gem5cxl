import m5
from m5.objects import *
from cache import *
import argparse

parser = argparse.ArgumentParser(description='A simple system with 2-level cache.')
parser.add_argument("binary", default="", nargs="?", type=str,
                    help="Path to the binary to execute.")
parser.add_argument("--l1i_size",
                    help=f"L1 instruction cache size. Default: 16kB.")
parser.add_argument("--l1d_size",
                    help="L1 data cache size. Default: Default: 64kB.")
parser.add_argument("--l2_size",
                    help="L2 cache size. Default: 256kB.")

options = parser.parse_args()
system = System()

system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '1GHz'
system.clk_domain.voltage_domain = VoltageDomain()
system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('512MB')]
system.cpu = TimingSimpleCPU()      
#其他选项是 RiscvTimingSimpleCPU ArmTimingSimpleCPU，这里先用x86吧，教程是这么用的


system.cpu.icache = L1ICache(options)
system.cpu.dcache = L1DCache(options)
#连接到cpu端口
system.cpu.icache.connectCPU(system.cpu)
system.cpu.dcache.connectCPU(system.cpu)
#l2缓存总线
system.l2bus = L2XBar()
system.cpu.icache.connectBus(system.l2bus)#l1连到l2总线
system.cpu.dcache.connectBus(system.l2bus)

system.membus = SystemXBar()
    
system.l2cache = L2Cache(options)
system.l2cache.connectCPUSideBus(system.l2bus)
system.l2cache.connectMemSideBus(system.membus)









#system.cpu.icache_port = system.membus.cpu_side_ports
#system.cpu.dcache_port = system.membus.cpu_side_ports
#其他可连的选项是，system.cpu.icache_port = system.l1_cache.cpu_side，这就是有l1缓存里。在memobejct会涉及更多，这里先照着教程用就行


#PIO 和中断端口连接到内存总线是 x86 特定的要求。其他 ISA（例如 ARM）不需要这 3 条额外的行。
system.cpu.createInterruptController()
system.cpu.interrupts[0].pio = system.membus.mem_side_ports
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports

system.system_port = system.membus.cpu_side_ports

#内存控制器
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports


binary = 'tests/test-progs/hello/bin/x86/linux/hello'

# for gem5 V21 and beyond, uncomment the following line
system.workload = SEWorkload.init_compatible(binary)

process = Process()
process.cmd = [binary]
system.cpu.workload = process
system.cpu.createThreads()


root = Root(full_system = False, system = system)
m5.instantiate()
print("Beginning simulation!")
exit_event = m5.simulate()

print('Exiting @ tick {} because {}'
      .format(m5.curTick(), exit_event.getCause()))