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
# 创建两个CPU
system.cpu = [TimingSimpleCPU(), TimingSimpleCPU()]
#总线
system.membus = SystemXBar()
for cpu in system.cpu:
    cpu.createInterruptController()
    cpu.isa=X86ISA()

for i in range(2):
    system.cpu[i].icache = L1ICache(options)
    system.cpu[i].dcache = L1DCache(options)
    system.cpu[i].icache.connectCPU(system.cpu[i])
    system.cpu[i].dcache.connectCPU(system.cpu[i])
    system.cpu[i].interrupts[0].pio = system.membus.mem_side_ports
    system.cpu[i].interrupts[0].int_requestor = system.membus.cpu_side_ports
    system.cpu[i].interrupts[0].int_responder = system.membus.mem_side_ports

# 将共享L2缓存
system.l2cache = L2Cache(options)
system.l2bus = L2XBar()
for i in range(2):
    system.cpu[i].icache.connectBus(system.l2bus)#l1连到l2总线
    system.cpu[i].dcache.connectBus(system.l2bus)

# 创建两个内存控制器

#第一个local memory
system.mem_ctrl0 = MemCtrl()
system.mem_ctrl0.dram = DDR3_1600_8x8()
system.mem_ctrl0.dram.range = AddrRange("8GB")

#第二个remote memory
system.mem_ctrl1 = MemCtrl()
system.mem_ctrl1.dram = DDR3_1600_8x8()
system.mem_ctrl1.dram.range = AddrRange("9GB","16GB")
# 将内存控制器连接到总线上
#system.membus = SystemXBar()
#连接L2缓存
system.l2cache.connectCPUSideBus(system.l2bus)
system.l2cache.connectMemSideBus(system.membus)
#连接端口
system.mem_ctrl0.port = system.membus.mem_side_ports
system.mem_ctrl1.port = system.membus.mem_side_ports

system.mem_ranges = [AddrRange('8GB')]


binary = './tests/sieve'
system.workload = SEWorkload.init_compatible(binary)
process = Process()
process.cmd = [binary]
for i in range(2):
    system.cpu[i].workload = process
    system.cpu[i].createThreads()

# 创建根节点
root = Root(full_system = False, system = system)

# 设置模拟开始点
m5.instantiate()

# 运行仿真直到结束
print("Beginning simulation!")
exit_event = m5.simulate()
print('Exiting @ tick {} because {}'
      .format(m5.curTick(), exit_event.getCause()))