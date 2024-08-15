from m5.objects import Cache


class L1Cache(Cache):
    assoc = 2 #缓存关联度
    tag_latency = 2 #标签比较延迟周期数
    data_latency = 2 #数据访问延迟周期数
    response_latency = 2 #响应延迟
    mshrs = 4 #最大贡献资源数
    tgts_per_mshr = 20 #每个mshrs的目标数量
    def __init__(self, options=None):
        super(L1Cache, self).__init__()
        pass
    def connectCPU(self, cpu):
        # need to define this in a base class!
        raise NotImplementedError
    def connectBus(self, bus):
        self.mem_side = bus.cpu_side_ports

class L1ICache(L1Cache):
    size = '16kB'

class L1DCache(L1Cache):
    size = '64kB'


class L2Cache(Cache):
    size = '256kB' #缓存大小
    assoc = 8
    tag_latency = 20
    data_latency = 20
    response_latency = 20
    mshrs = 20
    tgts_per_mshr = 12
    def __init__(self, options=None):
        super(L2Cache, self).__init__()
        if not options or not options.l2_size:
            return
        self.size = options.l2_size
    def connectCPUSideBus(self, bus):
        self.cpu_side = bus.mem_side_ports

    def connectMemSideBus(self, bus):
        self.mem_side = bus.cpu_side_ports

class L1ICache(L1Cache):
    size = '16kB'
    def __init__(self, options=None):
        super(L1ICache, self).__init__(options)
        if not options or not options.l1i_size:
            return
        self.size = options.l1i_size
    def connectCPU(self, cpu):
        self.cpu_side = cpu.icache_port

class L1DCache(L1Cache):
    size = '64kB'
    def __init__(self, options=None):
        super(L1DCache, self).__init__(options)
        if not options or not options.l1d_size:
            return
        self.size = options.l1d_size
    def connectCPU(self, cpu):
        self.cpu_side = cpu.dcache_port


