
import subprocess
from math import ceil
from os.path import basename, join, splitext
from time import sleep
import json
import os

from threading import Thread

from benchmark.commands import CommandMaker
from benchmark.config import Key, LocalCommittee, NodeParameters, BenchParameters, ConfigError
from benchmark.logs import LogParser, ParseError
from benchmark.utils import Print, BenchError, PathMaker


class LocalBench:
    BASE_PORT = 9000

    def __init__(self, bench_parameters_dict, node_parameters_dict):
        try:
            self.bench_parameters = BenchParameters(bench_parameters_dict)
            self.node_parameters = NodeParameters(node_parameters_dict)
        except ConfigError as e:
            raise BenchError('Invalid nodes or bench parameters', e)

    def __getattr__(self, attr):
        return getattr(self.bench_parameters, attr)

    def _background_run(self, command, log_file):
        name = splitext(basename(log_file))[0]
        cmd = f'{command} 2> {log_file}'
        subprocess.run(['tmux', 'new', '-d', '-s', name, cmd], check=True)

    def _kill_nodes(self):
        try:
            cmd = CommandMaker.kill().split()
            subprocess.run(cmd, stderr=subprocess.DEVNULL)
        except subprocess.SubprocessError as e:
            raise BenchError('Failed to kill testbed', e)

    def _kill_faulty(self, id, duration):
        print(f'replica {id} is faulty and will be crashed after {duration}s execution')
        sleep(duration)
        subprocess.run(['tmux', 'kill-session', '-t', f'node-{id}'])
        subprocess.run(['tmux', 'kill-session', '-t', f'client-{id}'])
        print(f'and replica {id} crashed after {duration}s exectution')
    
    # def _delay(self, node_i, delay, delay_duration):
    #     sleep(10)  # grace period
    #     print(f'Communication delay for server {node_i} increases to {delay}ms for duration {delay_duration}s')
    #     subprocess.run(f'tc qdisc add dev eth0 root netem delay {delay}ms', shell = True)# specification about delay distribution 
    #     # subprocess.run(f'tc qdisc add dev lo root netem delay {delay}ms {round(delay/10)}ms distribution normal', shell = True)# specification about delay distribution 
    #     sleep(delay_duration)
    #     subprocess.run('tc qdisc del dev eth0 root', shell=True)
    #     # subprocess.run('tc qdisc del dev lo root', shell=True)
    #     print(f'Communication delay for server {node_i} ends after {delay_duration}s')

    def _delay(self, node_i, delay, delay_start, duration):
        sleep(delay_start)  # grace period
        print(f'Communication delay for server {node_i} increases to {delay}ms for {delay_start}s')
        subprocess.run(f'tc qdisc add dev eth0 root netem delay {delay}ms', shell = True)# specification about delay distribution 
        # subprocess.run(f'tc qdisc add dev lo root netem delay {delay}ms {round(delay/10)}ms distribution normal', shell = True)# specification about delay distribution 
        sleep(duration - delay_start)
        subprocess.run('tc qdisc del dev eth0 root', shell=True)
        # subprocess.run('tc qdisc del dev lo root', shell=True)
        print(f'Communication delay for server {node_i} ends')    
    
    def _partition(self, targets, start, end):
        print(f'{start}s normal network before partition')
        sleep(start)
        print(f'Partition into two networks happened for {end}s ')
        
        # os.popen('tc qdisc del dev eth0 root')
        os.popen('tc qdisc add dev eth0 root handle 1: prio')
        os.popen('tc qdisc add dev eth0 parent 1:3 handle 30: netem loss 100%')
        for tar in targets:
            os.popen(f'tc filter add dev eth0 protocol ip parent 1:0 prio 3 u32 match ip dst {tar} flowid 1:3')
        sleep(end)
        os.popen('tc qdisc del dev eth0 root')

    def run(self, debug=False):
        assert isinstance(debug, bool)
        Print.heading('Starting local benchmark')

        # Kill any previous testbed.
        self._kill_nodes()

        try:
            Print.info('Setting up testbed...')
            Print.info('Reading configuration...')
        
            # print(self.nodes)
            nodes, rate, local, servers, replicas, parsing, duration, faults, S2f, delay, partition = self.nodes[0], self.rate[0], self.local, self.servers, self.replicas, self.parsing, self.duration, self.faults, self.S2f, self.delay, self.partition
            
            
            # Cleanup all files.
            cmd = f'{CommandMaker.clean_logs()} ; {CommandMaker.cleanup()}'
            subprocess.run([cmd], shell=True, stderr=subprocess.DEVNULL)
            sleep(0.5) # Removing the store may take time.

            # Recompile the latest code.
            print("For the first running, compilation halts a little longer")
            cmd = CommandMaker.compile().split()
            subprocess.run(cmd, check=True, cwd=PathMaker.node_crate_path())

            # Create alias for the client and nodes binary.
            cmd = CommandMaker.alias_binaries(PathMaker.binary_path())
            subprocess.run([cmd], shell=True)

            # Generate configuration files.
            keys = []
            key_files = [PathMaker.key_file(i) for i in range(nodes)]
            for filename in key_files:
                cmd = CommandMaker.generate_key(filename).split()
                #if local == 1:  
                #    subprocess.run(cmd, check=True)
                keys += [Key.from_file(filename)]
            with open('index.txt') as f:
                node_i = int(f.readline())
                f.close()
            node_ip = '127.0.0.1'
            if node_i == 0:
                node_ip = '129.13.88.182'
            elif node_i == 1:
                node_ip = '129.13.88.183'
            elif node_i == 2 :
                node_ip = '129.13.88.184'
            elif node_i == 3:
                node_ip = '129.13.88.185'
            elif node_i == 4:
                node_ip = '129.13.88.186'
            elif node_i == 5:
                node_ip = '129.13.88.187'
            elif node_i == 6:
                node_ip = '129.13.88.188'
            elif node_i == 7:
                node_ip = '129.13.88.189'
            elif node_i == 8:
                node_ip = '129.13.88.190'
            elif node_i == 9:
                node_ip = '129.13.88.180'
            ips = ['129.13.88.182', '129.13.88.183', '129.13.88.184', '129.13.88.185', '129.13.88.186', '129.13.88.187', '129.13.88.188', '129.13.88.189', '129.13.88.190', '129.13.88.180']

            # node_ip = ips[node_i]

            names = [x.name for x in keys]
            committee = LocalCommittee(names, self.BASE_PORT, local, servers)
            committee.print(PathMaker.committee_file())

            self.node_parameters.print(PathMaker.parameters_file())

            # Do not boot faulty nodes.
            # nodes = nodes - self.faults

            # Run the clients (they will wait for the nodes to be ready).
            addresses = committee.front
            rate_share = ceil(rate / nodes)
          
            timeout = self.node_parameters.timeout_delay
            client_logs = [PathMaker.client_log_file(i) for i in range(nodes)]
            if local == 0:             
                for addr, log_file in zip(addresses, client_logs):
                    addr_ip = addr[:-5]
                    #print(addr_ip)
                    #print(addr)
                    if addr_ip == node_ip:
                        cmd = CommandMaker.run_client(
                        addr,
                        self.tx_size,
                        rate_share,
                        timeout)   # check this in rust
                        # print("!!!!!!!")
                        # print(cmd)
                        self._background_run(cmd, log_file)

            if local == 1:
                for addr, log_file in zip(addresses, client_logs):
                    #print(addr)
                    cmd = CommandMaker.run_client(
                        addr,
                        self.tx_size,
                        rate_share,
                        timeout
                    )
                    # print(cmd)
                    self._background_run(cmd, log_file)

            # Run the nodes.
            dbs = [PathMaker.db_path(i) for i in range(nodes)]
            node_logs = [PathMaker.node_log_file(i) for i in range(nodes)]
            if local == 0:
                index = 0
                for key_file, db, log_file in zip(key_files, dbs, node_logs):
                    #print(key_file)
                    if index % 10 == node_i:
                        cmd = CommandMaker.run_node(
                        key_file,
                        PathMaker.committee_file(),
                        db,
                        PathMaker.parameters_file(),
                        debug=debug
                        )
                        # print(cmd)
                        self._background_run(cmd, log_file)
                    index = index + 1

            if local == 1:
                for key_file, db, log_file in zip(key_files, dbs, node_logs):
                    cmd = CommandMaker.run_node(
                        key_file,
                        PathMaker.committee_file(),
                        db,
                        PathMaker.parameters_file(),
                        debug=debug
                    )
                    # print(cmd)
                    self._background_run(cmd, log_file)


            # Wait for the nodes to synchronize
            Print.info('Waiting for the nodes to synchronize...')
            #sleep(2 * self.node_parameters.timeout_delay / 1000)
            sleep(2 * timeout / 1000)
            # Wait for all transactions to be processed.
            Print.info(f'Running benchmark ({duration} sec)...')
            
            if faults > 0 and S2f == False and delay == 0 and partition == False:
                with open('faulty.json') as f:
                    faulty_config = json.load(f)
                    f.close()
                
                for r in range(replicas):
                    replica_i = node_i + r * servers 
                    flag = faulty_config[f'{replica_i}'][0]
                    if flag == 1:
                        faulty_duration = faulty_config[f'{replica_i}'][1]
                        Thread(target=self._kill_faulty, args=(replica_i,faulty_duration)).start()

            if faults >= 0 and S2f == True and delay == 0 and partition == False:
                if faults > 0:
                    with open('faulty.json') as f:
                        faulty_config = json.load(f)
                        f.close()
                    
                    for r in range(replicas):
                        replica_i = node_i + r * servers 
                        flag = faulty_config[f'{replica_i}'][0]
                        if flag == 1:
                            faulty_duration = 5
                            Thread(target=self._kill_faulty, args=(replica_i,faulty_duration)).start()
                else:
                    print("All replicas are correct")

            elif delay > 0 and faults == 0 and S2f == False and partition == False:
                with open('delay.json') as f:
                    delay_config = json.load(f)
                    f.close()
                if delay_config[f'{node_i}'][0] == 1:
                    # Thread(target=self._delay, args=(node_i, delay_config[f'{node_i}'][1], delay_config[f'{node_i}'][2])).start()
                    Thread(target=self._delay, args=(node_i, delay_config[f'{node_i}'][1], delay_config[f'{node_i}'][2], duration)).start()
                    # self._delay(node_i, delay_config[f'{node_i}'][1], delay_config[f'{node_i}'][2])
        
            elif partition == True and faults == 0 and delay == 0:
                with open('partition.json') as f:
                    partition_config = json.load(f)
                    f.close()
                    targets = []
                    for node in range(servers):
                        if partition_config[f'{node_i}'][0] != partition_config[f'{node}'][0]:
                            targets.append(ips[node])
                    Thread(target=self._partition, args=(targets, partition_config[f'{node_i}'][1], partition_config[f'{node_i}'][2])).start()

            # Thread(target=self._delay,args=(3000,1000,5)).start()
            sleep(duration)
            self._kill_nodes()
            

            # Parse logs and return the parser.
            
            return LogParser.process('./logs', faults=self.faults)

        except (subprocess.SubprocessError, ParseError) as e:
            self._kill_nodes()
            raise BenchError('Failed to run benchmark', e)
