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
# 创建一个系统实例
system = System()

# 设置系统时钟频率
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '1GHz'
system.clk_domain.voltage_domain = VoltageDomain()
system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('8192MB')]

system.cpu = X86TimingSimpleCPU()

system.cpu.interrupts[0].pio = system.membus.mem_side_ports
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports

system.membus = SystemXBar()

system.cpu.createInterruptController()

system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports
system.system_port = system.membus.cpu_side_ports

#创建pcie
system.pcie1 = PCIELink(lanes = 2, speed = 5, mps=5, max_queue_size= 10)

system.RootComplex = RootComplex()
system.switch = PCIESwitch()

system.RootComplex.host =system.cpu.pcie_root_ports
system.RootComplex.response = system.membus.mem_side_ports
system.RootComplex.request_dma = system.membus.cpu_side_ports

system.RootComplex.response_dma1 = system.pcie1.upstreamRequest
system.RootComplex.request1    = system.pcie1.upstreamResponse 

system.pcie1.downstreamRequest  = system.switch.response
system.pcie1.downstreamResponse = system.switch.request_dma

binary = './tests/sieve'
system.workload = SEWorkload.init_compatible(binary)
process = Process()
process.cmd = [binary]

system.cpu.workload =process
system.cpu.createThreads()


# 创建根节点
root = Root(full_system = False, system = system)

# 设置模拟开始点
m5.instantiate()

# 运行仿真直到结束
print("Beginning simulation!")
exit_event = m5.simulate()
print('Exiting @ tick {} because {}'
      .format(m5.curTick(), exit_event.getCause()))