import m5
from m5.objects import *


system = System()

system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '1GHz'
system.clk_domain.voltage_domain = VoltageDomain()

system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('8192MB')]

#system.cpu = X86TimingSimpleCPU()
system.cpu=TimingSimpleCPU()
#其他选项是 RiscvTimingSimpleCPU ArmTimingSimpleCPU，这里先用x86吧，教程是这么用的


system.membus = SystemXBar()



system.cpu.icache_port = system.membus.cpu_side_ports
system.cpu.dcache_port = system.membus.cpu_side_ports
#其他可连的选项是，system.cpu.icache_port = system.l1_cache.cpu_side，这就是有l1缓存里。在memobejct会涉及更多，这里先照着教程用就行


system.cpu.createInterruptController()
# system.cpu.interrupts[0].pio = system.membus.mem_side_ports
# system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
# system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports
system.system_port = system.membus.cpu_side_ports


system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports


binary = 'tests/test-progs/hello/bin/arm/linux/hello'
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
