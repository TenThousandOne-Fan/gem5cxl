import m5
from m5.objects import *
from cache import *

system=System()

# 设置系统时钟频率
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '1GHz'
system.clk_domain.voltage_domain = VoltageDomain()
system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('8192MB')]

system.cpu0=TimingSimpleCPU()
system.cpu1=TimingSimpleCPU()
#总线
system.membus = SystemXBar()

system.cpu0.icache_port = system.membus.cpu_side_ports
system.cpu0.dcache_port = system.membus.cpu_side_ports

system.cpu0.createInterruptController()

system.cpu0.interrupts[0].pio = system.membus.mem_side_ports
system.cpu0.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu0.interrupts[0].int_responder = system.membus.mem_side_ports

system.system_port = system.membus.cpu_side_ports


system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports
#IO总线
system.iobus=IOXBar()
system.brideg=Bridge(delay="50ns")

# system.pcidevice=PciDevice()
# system.pcidevice.pci_bus=system.iobus.mem_side_ports
# system.pcidevice.host=system.iobus.master
system.pcibus = NoncoherentXBar(width=16)
system.pcibus.clk_domain = SrcClockDomain()
system.pcibus.clk_domain.clock = '33MHz'
system.pcibus.clk_domain.voltage_domain = VoltageDomain()

system.membus.mem_side_ports = system.pcibus.cpu_side_ports
system.pcibus.mem_side_ports = system.membus.cpu_side_ports

system.pcidev=PciDevice()
system.pcidev.pio = system.pcibus.mem_side_ports
system.pcidev.dma = system.membus.cpu_side_ports
# binary = "tests/test-progs/hello/bin/x86/linux/hello"

# system.workload = SEWorkload.init_compatible(binary)

# # Create a process for a simple "Hello World" application
# process = Process()
# # Set the command
# # cmd is a list which begins with the executable (like argv)
# process.cmd = [binary]
# # Set the cpu to use the process as its workload and create thread contexts
# system.cpu0.workload = process
# system.cpu0.createThreads()

# set up the root SimObject and start the simulation
root = Root(full_system=False, system=system)
# instantiate all of the objects we've created above
m5.instantiate()

print("Beginning simulation!")
exit_event = m5.simulate()
print("Exiting @ tick %i because %s" % (m5.curTick(), exit_event.getCause()))

