from http import server
from json import dump, load
import re
from traceback import print_tb


class ConfigError(Exception):
    pass


class Key:
    def __init__(self, name, secret):
        self.name = name
        self.secret = secret

    @classmethod
    def from_file(cls, filename):
        assert isinstance(filename, str)
        with open(filename, 'r') as f:
            data = load(f)
        return cls(data['name'], data['secret'])


class Committee:
    def __init__(self, names, consensus_addr, front_addr, mempool_addr):
        inputs = [names, consensus_addr, front_addr, mempool_addr]
        assert all(isinstance(x, list) for x in inputs)
        assert all(isinstance(x, str) for y in inputs for x in y)
        assert len({len(x) for x in inputs}) == 1

        self.names = names
        self.consensus = consensus_addr
        self.front = front_addr
        self.mempool = mempool_addr

        self.json = {
            'consensus': self._build_consensus(),
            'mempool': self._build_mempool()
        }

    def _build_consensus(self):
        node = {}
        for a, n in zip(self.consensus, self.names):
            node[n] = {'name': n, 'stake': 1, 'address': a}
        return {'authorities': node, 'epoch': 1}

    def _build_mempool(self):
        node = {}
        for n, f, m in zip(self.names, self.front, self.mempool):
            node[n] = {'name': n, 'front_address': f, 'mempool_address': m}
        return {'authorities': node, 'epoch': 1}

    def print(self, filename):
        assert isinstance(filename, str)
        with open(filename, 'w') as f:
            dump(self.json, f, indent=4, sort_keys=True)

    def size(self):
        return len(self.json['consensus']['authorities'])

    @classmethod
    def load(cls, filename):
        assert isinstance(filename, str)
        with open(filename, 'r') as f:
            data = load(f)

        consensus_authorities = data['consensus']['authorities'].values()
        mempool_authorities = data['mempool']['authorities'].values()

        names = [x['name'] for x in consensus_authorities]
        consensus_addr = [x['address'] for x in consensus_authorities]
        front_addr = [x['front_address'] for x in mempool_authorities]
        mempool_addr = [x['mempool_address'] for x in mempool_authorities]
        return cls(names, consensus_addr, front_addr, mempool_addr)


class LocalCommittee(Committee):
    def __init__(self, names, port, local, servers):
        assert isinstance(names, list) and all(isinstance(x, str) for x in names)
        assert isinstance(port, int)
        size = len(names)


        consensus = []
        front = []
        mempool = []
        
        if local == True:
            consensus = [f'127.0.0.1:{port + i}' for i in range(size)]
            front = [f'127.0.0.1:{port + i + size}' for i in range(size)]
            mempool = [f'127.0.0.1:{port + i + 2*size}' for i in range(size)]
  
        if local == False:
            for i in range(size):

                if i % servers != (servers-1):
                    #consensus[i] = 129.13.88.1{(i % 10) +82}
                    consensus.append(f'129.13.88.1{(i % servers) +82}:{port }')
                    front.append(f'129.13.88.1{(i % servers) +82}:{port + 1}')
                    mempool.append(f'129.13.88.1{(i % servers) +82}:{port + 2}')
                if i % servers == (servers-1):
                    consensus.append(f'129.13.88.1{(i % servers) +71}:{port}')
                    front.append(f'129.13.88.1{(i % servers) +71}:{port + 1}')
                    mempool.append(f'129.13.88.1{(i % servers) +71}:{port +2}')
                    port = port + 3
        
        super().__init__(names, consensus, front, mempool)
        


class NodeParameters:
    def __init__(self, json):
        inputs = []
        try:
            inputs += [json['consensus']['timeout_delay']]
            inputs += [json['consensus']['sync_retry_delay']]
            inputs += [json['consensus']['max_payload_size']]
            inputs += [json['consensus']['min_block_delay']]
            inputs += [json['mempool']['queue_capacity']]
            inputs += [json['mempool']['sync_retry_delay']]
            inputs += [json['mempool']['max_payload_size']]
            inputs += [json['mempool']['min_block_delay']]
        except KeyError as e:
            raise ConfigError(f'Malformed parameters: missing key {e}')

        if not all(isinstance(x, int) for x in inputs):
            raise ConfigError('Invalid parameters type')

        self.timeout_delay = json['consensus']['timeout_delay'] 
        self.json = json

    def print(self, filename):
        assert isinstance(filename, str)
        with open(filename, 'w') as f:
            dump(self.json, f,  indent=4, sort_keys=True)


class BenchParameters:
    def __init__(self, json):
        try:
            nodes = json['nodes']
            nodes = json['servers'] * json['replicas']
            nodes = nodes if isinstance(nodes, list) else [nodes]
            if not nodes or any(x <= 0 for x in nodes):
                raise ConfigError('Missing or invalid number of nodes')

            rate = json['rate'] 
            rate = rate if isinstance(rate, list) else [rate]
            if not rate:
                raise ConfigError('Missing input rate')

            self.nodes = [int(x) for x in nodes]
            self.rate = [int(x) for x in rate]
            self.tx_size = int(json['tx_size'])
            self.faults = int(json['faults'])
            self.duration = int(json['duration'])
            self.runs = int(json['runs']) if 'runs' in json else 1
            
            self.local = bool(json['local'])
            self.servers = int(json['servers'])
            self.replicas = int(json['replicas'])
            self.parsing = bool(json['parsing'])
            self.delay = int(json['delay'])
            self.offset = int(json['offset'])
        except KeyError as e:
            raise ConfigError(f'Malformed bench parameters: missing key {e}')

        except ValueError:
            raise ConfigError('Invalid parameters type')

        if min(self.nodes) <= self.faults:
            raise ConfigError('There should be more nodes than faults')


class PlotParameters:
    def __init__(self, json):
        try:
            nodes = json['nodes'] 
            nodes = nodes if isinstance(nodes, list) else [nodes]
            if not nodes:
                raise ConfigError('Missing number of nodes')
            self.nodes = [int(x) for x in nodes]

            self.tx_size = int(json['tx_size'])

            faults = json['faults'] 
            faults = faults if isinstance(faults, list) else [faults]
            self.faults = [int(x) for x in faults] if faults else [0]

            max_lat = json['max_latency'] 
            max_lat = max_lat if isinstance(max_lat, list) else [max_lat]
            if not max_lat:
                raise ConfigError('Missing max latency')
            self.max_latency = [int(x) for x in max_lat]

        except KeyError as e:
            raise ConfigError(f'Malformed bench parameters: missing key {e}')

        except ValueError:
            raise ConfigError('Invalid parameters type')

