from audioop import add
import subprocess
from math import ceil
from os.path import basename, join, splitext
from time import sleep

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

    def run(self, debug=False):
        assert isinstance(debug, bool)
        Print.heading('Starting local benchmark')

        # Kill any previous testbed.
        self._kill_nodes()

        try:
            Print.info('Setting up testbed...')
            print(self.nodes)
            nodes, rate, replicas, local, servers = self.nodes[0], self.rate[0], self.replicas, self.local, self.servers
            nodes = replicas * servers
            #print(type(local))
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
            node_i = int(subprocess.check_output(['tail', '-1', 'index.txt']))
            node_ip = '127.0.0.1'
            
            match node_i:
                case 0: node_ip = '129.13.88.182'
                case 1: node_ip = '129.13.88.183'
                case 2: node_ip = '129.13.88.184'
                case 3: node_ip = '129.13.88.185'
                case 4: node_ip = '129.13.88.186'
                case 5: node_ip = '129.13.88.187'
                case 6: node_ip = '129.13.88.188'
                case 7: node_ip = '129.13.88.189'
                case 8: node_ip = '129.13.88.190' 
                case 9: node_ip = '129.13.88.180'
            #print(node_ip)
            names = [x.name for x in keys]
            #print(f'names: {names}')
            committee = LocalCommittee(names, self.BASE_PORT, nodes, local, servers)
            committee.print(PathMaker.committee_file())

            self.node_parameters.print(PathMaker.parameters_file())

            # Do not boot faulty nodes.
            nodes = nodes - self.faults

            # Run the clients (they will wait for the nodes to be ready).
            addresses = committee.front
            #print(addresses)
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
                        timeout)
                        print("!!!!!!!")
                        print(cmd)
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
                    print(cmd)
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
                        print(cmd)
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
                    print(cmd)
                    self._background_run(cmd, log_file)

            # Wait for the nodes to synchronize
            Print.info('Waiting for the nodes to synchronize...')
            sleep(2 * self.node_parameters.timeout_delay / 1000)

            # Wait for all transactions to be processed.
            Print.info(f'Running benchmark ({self.duration} sec)...')
            sleep(self.duration)
            self._kill_nodes()

            # Parse logs and return the parser.
            Print.info('Parsing logs...')
            return LogParser.process('./logs', faults=self.faults)

        except (subprocess.SubprocessError, ParseError) as e:
            self._kill_nodes()
            raise BenchError('Failed to run benchmark', e)
