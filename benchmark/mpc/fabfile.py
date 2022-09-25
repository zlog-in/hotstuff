
from fabric import ThreadingGroup, Connection
from fabric import task
import subprocess
from datetime import datetime
import random
import json
import os

import sqlite3
from statistics import mean


@task
def benchmarking(ctx):
    hosts = ThreadingGroup('mpc-0','mpc-1','mpc-2','mpc-3','mpc-4','mpc-5','mpc-6','mpc-7','mpc-8','mpc-9')
    hosts.run('docker stop narwhal')
    hosts.run('docker start hotstuff')
    hosts.put(f'{os.pardir}/config.json', remote  = '/home/zhan/hotstuff/')
    hosts.put(f'{os.pardir}/.parameters.json', remote  = '/home/zhan/hotstuff/')
    hosts.run('docker cp hotstuff/config.json hotstuff:/home/hotstuff/benchmark/')
    hosts.run('docker cp hotstuff/.parameters.json hotstuff:/home/hotstuff/benchmark/')
    hosts.run('docker exec -t hotstuff bash ben.sh')

@task
def faulty(ctx):
    hosts = ThreadingGroup('mpc-0','mpc-1','mpc-2','mpc-3','mpc-4','mpc-5','mpc-6','mpc-7','mpc-8','mpc-9')
    faulty_config()
    hosts.run('docker stop narwhal')
    hosts.run('docker start hotstuff')

    hosts.put(f'{os.pardir}/faulty.json', remote  = '/home/zhan/hotstuff/')
    hosts.put(f'{os.pardir}/delay.json', remote  = '/home/zhan/hotstuff/')
    hosts.put(f'{os.pardir}/bench_parameters.json', remote  = '/home/zhan/hotstuff/')
    hosts.put(f'{os.pardir}/node_parameters.json', remote  = '/home/zhan/hotstuff/')
    hosts.run('docker cp hotstuff/faulty.json hotstuff:/home/hotstuff/benchmark/')
    hosts.run('docker cp hotstuff/delay.json hotstuff:/home/hotstuff/benchmark/')
    hosts.run('docker cp hotstuff/bench_parameters.json hotstuff:/home/hotstuff/benchmark/')
    hosts.run('docker cp hotstuff/node_parameters.json hotstuff:/home/hotstuff/benchmark/')

    hosts.run('docker exec -t hotstuff bash ben.sh')

@task
def timeout(ctx):
    hosts = ThreadingGroup('mpc-0','mpc-1','mpc-2','mpc-3','mpc-4','mpc-5','mpc-6','mpc-7','mpc-8','mpc-9')
    delay_config()
    hosts.run('docker stop narwhal')
    hosts.run('docker start hotstuff')
    # # hosts.put(f'{os.pardir}/config.json', remote  = '/home/zhan/hotstuff/')
    # # hosts.put(f'{os.pardir}/.parameters.json', remote  = '/home/zhan/hotstuff/')
    # hosts.put(f'{os.pardir}/faulty.json', remote  = '/home/zhan/hotstuff/')
    
    hosts.put(f'{os.pardir}/bench_parameters.json', remote  = '/home/zhan/hotstuff/')
    hosts.put(f'{os.pardir}/node_parameters.json', remote  = '/home/zhan/hotstuff/')
    hosts.put(f'{os.pardir}/delay.json', remote  = '/home/zhan/hotstuff/')
    hosts.put(f'{os.pardir}/faulty.json', remote  = '/home/zhan/hotstuff/')
    # hosts.run('docker cp hotstuff/faulty.json hotstuff:/home/hotstuff/benchmark/')
    hosts.run('docker cp hotstuff/bench_parameters.json hotstuff:/home/hotstuff/benchmark/')
    hosts.run('docker cp hotstuff/node_parameters.json hotstuff:/home/hotstuff/benchmark/')
    hosts.run('docker cp hotstuff/delay.json hotstuff:/home/hotstuff/benchmark/')
    hosts.run('docker cp hotstuff/faulty.json hotstuff:/home/hotstuff/benchmark/')
    

    hosts.run('docker exec -t hotstuff bash ben.sh')

@task
def partition(ctx):
    hosts = ThreadingGroup('mpc-0','mpc-1','mpc-2','mpc-3','mpc-4','mpc-5','mpc-6','mpc-7','mpc-8','mpc-9')
    partition_config()
    # hosts.run('docker stop narwhal')
    # hosts.run('docker start hotstuff')
   
    
    # hosts.put(f'{os.pardir}/bench_parameters.json', remote  = '/home/zhan/hotstuff/')
    # hosts.put(f'{os.pardir}/node_parameters.json', remote  = '/home/zhan/hotstuff/')
    # hosts.put(f'{os.pardir}/delay.json', remote  = '/home/zhan/hotstuff/')
    # hosts.put(f'{os.pardir}/faulty.json', remote  = '/home/zhan/hotstuff/')
    # hosts.put(f'{os.pardir}/partition.json', remote  = '/home/zhan/hotstuff/')
    
    # hosts.run('docker cp hotstuff/bench_parameters.json hotstuff:/home/hotstuff/benchmark/')
    # hosts.run('docker cp hotstuff/node_parameters.json hotstuff:/home/hotstuff/benchmark/')
    # hosts.run('docker cp hotstuff/delay.json hotstuff:/home/hotstuff/benchmark/')
    # hosts.run('docker cp hotstuff/faulty.json hotstuff:/home/hotstuff/benchmark/')
    # hosts.run('docker cp hotstuff/partition.json hotstuff:/home/hotstuff/benchmark/')

    # hosts.run('docker exec -t hotstuff bash ben.sh')


@task
def container(ctx):
    hosts = ThreadingGroup('mpc-0','mpc-1','mpc-2','mpc-3','mpc-4','mpc-5','mpc-6','mpc-7','mpc-8','mpc-9')
    hosts.run('rm -rf hotstuff/logs/')
    hosts.run('mkdir -p hotstuff/logs')
    cwd = os.getcwd()
    
    hosts.put(f'{cwd}/ben.sh', remote='/home/zhan/hotstuff')
    hosts.put(f'{cwd}/update.sh', remote='/home/zhan/hotstuff')
    hosts.run('docker stop narwhal')
    hosts.run('docker rm -f hotstuff')
    hosts.run('docker run -itd --cap-add=NET_ADMIN --name hotstuff -p 9000-9049:9000-9049 --mount type=bind,source=/home/zhan/hotstuff/logs,destination=/home/hotstuff/benchmark/logs image_hotstuff')
    
    hosts.run('docker cp index.txt hotstuff:/home/hotstuff/benchmark/')
    hosts.run('docker cp hotstuff/ben.sh hotstuff:/home/hotstuff/benchmark/')
    hosts.run('docker cp hotstuff/update.sh hotstuff:/home/hotstuff/benchmark/')
    hosts.run('docker exec -t hotstuff bash update.sh')

@task
def parsing(ctx):
    subprocess.call(['bash', '../parsing.sh'])

@task
def getdb(ctx):
    host = Connection('checker')
    host.get('/home/zhan/hotstuff/benchmark/mpc/results.db', local = f'{os.getcwd()}/results/')

@task
def build(ctx):
    hosts = ThreadingGroup('mpc-0','mpc-1','mpc-2','mpc-3','mpc-4','mpc-5','mpc-6','mpc-7','mpc-8','mpc-9')
    hosts.run('rm -rf hotstuff/')
    hosts.run('mkdir  hotstuff/')
    
    hosts.put(f'{os.getcwd()}/Dockerfile', remote='/home/zhan/hotstuff')
    hosts.run('docker rm -f hotstuff')
    hosts.run('docker rmi image_hotstuff')
    hosts.run('docker build -f /home/zhan/hotstuff/Dockerfile -t image_hotstuff .')


@task
def checker(ctx):
    host = Connection('checker')
    host.put('./checker.py', remote='hotstuff/benchmark/mpc/')
   
@task
def getresult(ctx):
    subprocess.call(['bash', '../getresult.sh'])


@task
def summary(ctx):
    with open('../bench_parameters.json') as f:
        bench_parameters = json.load(f)
        f.close()

    with open('../node_parameters.json') as f:
        node_parameters = json.load(f)
        f.close()
    consensus_bytes_list = []
    consensus_start_list = []
    consensus_end_list = []
    consensus_latency_list = []
    consensus_size_list = []
    
    end2end_bytes_list = []
    end2end_start_list = []
    end2end_end_list = []
    end2end_latency_list = []
    end2end_size_list = []
    
    for node_i in range(bench_parameters['servers']):
        with open(f'../logs/result-{node_i}.json') as f:
            result = json.load(f)
            f.close()
            consensus_bytes_list.append(result['consensus_bytes'])
            consensus_start_list.append(result['consensus_start'])
            consensus_end_list.append(result['consensus_end'])
            consensus_latency_list.append(result['consensus_latency'])
            consensus_size_list.append(result['consensus_size'])
    
            end2end_bytes_list.append(result['end2end_bytes'])
            end2end_start_list.append(result['end2end_start'])
            end2end_end_list.append(result['end2end_end'])
            end2end_latency_list.append(result['end2end_latency'])
            end2end_size_list.append(result['end2end_size'])
            
    
    

    consensus_duration = max(consensus_end_list) - min(consensus_start_list)
    end2end_duration = max(end2end_end_list) - min(end2end_start_list)
    print(f'total consensus duration: {consensus_duration}')
    print(f'total end2edn duration: {end2end_duration}')
    
    consensus_bps = (sum(consensus_bytes_list)) / consensus_duration
    end2end_bps = (sum(end2end_bytes_list)) / end2end_duration

    consensus_tps = consensus_bps / mean(consensus_size_list)
    end2end_tps = end2end_bps / mean(end2end_size_list)
 


    consensus_latency = mean(consensus_latency_list)
    end2end_latency = mean(end2end_latency_list)
  



    replicas = bench_parameters['replicas']
    servers = bench_parameters['servers']
    local = bench_parameters['local'] 
    duration = bench_parameters['duration']  
    rate = bench_parameters['rate'] 
    faults = bench_parameters['faults']
    delay = bench_parameters['delay']
    
    nodes = replicas * servers
    time_out = node_parameters['consensus']['timeout_delay']
    sync_retry = node_parameters['mempool']['sync_retry_delay']
    
    
    results_db = sqlite3.connect('./results.db')
    if faults == 0 and delay == 0:
        time_seed = datetime.now()
        insert_S1Hotstuff_results = f'INSERT INTO S1Hotstuff VALUES ("{time_seed}", {local}, {nodes}, {faults}, {time_out}, {sync_retry}, {duration}, {rate}, {round(consensus_tps)}, {round(consensus_latency)}, {round(end2end_latency)})'
        results_db.cursor().execute(insert_S1Hotstuff_results)
        results_db.commit()
        results_db.close()
    
    elif faults > 0 and delay ==0:
        with open('../faulty.json') as f:
            faulty_config = json.load(f)
            f.close()
        time_seed = faulty_config['time_seed']
        insert_S2Hotstuff_results = f'INSERT INTO S2Hotstuff VALUES ("{time_seed}", {local}, {nodes}, {faults}, {time_out}, {sync_retry}, {duration}, {rate}, {round(consensus_tps)}, {round(consensus_latency)}, {round(end2end_latency)})'
        results_db.cursor().execute(insert_S2Hotstuff_results)
        results_db.commit()
        results_db.close()
    
    elif delay > 0 and faults == 0:
        print("S3")

def faulty_config():


    with open('../bench_parameters.json', 'r') as f:
        bench_parameters = json.load(f)
        f.close()
    faults = bench_parameters['faults']
    servers = bench_parameters['servers']
    duration = bench_parameters['duration']
    replicas = bench_parameters['replicas']
    faulty_servers = set()
    time_seed = datetime.now()
    random.seed(time_seed)
    if faults != 0:
        while len(faulty_servers) != faults:
            faulty_servers.add(random.randrange(0, servers*replicas))
        print(f'{faults} out of {replicas*servers} replicas are randomly selected as faulty: {faulty_servers}')
    else:
        print("All replicas are non-faulty")
    
    with open('../faulty.json', 'w') as f:
        json.dump({f'{idx}': [0,0] for idx in range(servers * replicas)}, f, indent=4)
        f.close()

    
    with open('../faulty.json', 'r') as f:
        faulty_config = json.load(f)
        f.close()

    
    while len(faulty_servers) != 0:
        idx = faulty_servers.pop()
        faulty_config[f'{idx}'][0] = 1
        faulty_config[f'{idx}'][1] = random.randrange(5,duration-10) #duration - 10
    
    with open('../faulty.json', 'w') as f:
        json.dump(faulty_config, f, indent=4)
        f.close()

    write_time(time_seed)

def delay_config():
    with open('../bench_parameters.json', 'r') as f:
        bench_parameters = json.load(f)
        f.close()
    servers = bench_parameters['servers']
    duration = bench_parameters['duration']
    delay = bench_parameters['delay']
    
    delay_servers = set()
    time_seed = datetime.now()
    random.seed(time_seed)
    while len(delay_servers) != servers:
        delay_servers.add(random.randrange(0, servers))
    
    with open('../delay.json', 'w') as f:
        json.dump({f'{idx}': [0,0,0] for idx in range(servers)}, f, indent=4)
        f.close()
    
    with open('../delay.json', 'r') as f:
        delay_config = json.load(f)
        f.close()
    while len(delay_servers) != 0 and delay >= 0:
        idx = delay_servers.pop()
        delay_config[f'{idx}'][0] = 1
        # delay_config[f'{idx}'][1] = random.randint(100, delay) if delay > 100 else random.randint(100, 10000)
        delay_config[f'{idx}'][1] = delay   # random.randint(round(delay/2), round(delay*3/2))
        delay_config[f'{idx}'][2] = 0   #random.randint(10, int(duration/2))

    with open('../delay.json', 'w') as f:
        json.dump(delay_config, f, indent=4)
        f.close()

    with open(f'../delay.json') as f:
        delay_config = json.load(f)
        f.close()
    delay_config.update({'time_seed': f'{time_seed}'})

    with open('../delay.json', 'w') as f:
        json.dump(delay_config, f, indent=4)
        f.close()
    print("delay configuration done")
    
def partition_config():
    with open('../bench_parameters.json', 'r') as f:
        bench_parameters = json.load(f)
        f.close()
    servers = bench_parameters['servers']
    duration = bench_parameters['duration']
    partition = bench_parameters['partition']

    

    if partition == False:
        print("No network partitions!")
    else:

        time_seed = datetime.now()
        random.seed(time_seed)
        subnet = set()
        start = random.randrange(5, duration-10)
        end = random.randrange(10, duration - start)
        with open('../partition.json', 'w') as f:
            json.dump({f'{idx}': [0, start, end] for idx in range(servers)}, f, indent=4)
            f.close()

        

        while len(subnet) != servers/2:
            subnet.add(random.randrange(0, servers))

        with open('../partition.json') as f:
            partition_config = json.load(f)
            f.close()
            partition_config.update({'time_seed': f'{time_seed}'})
        
        for sub in subnet:
            partition_config[f'{sub}'][0] = 1

        with open('../partition.json', 'w')  as f:
            json.dump(partition_config, f, indent= 4)
        


def write_time(seed):
    with open(f'../faulty.json') as f:
        faulty_config = json.load(f)
        f.close()
    faulty_config.update({'time_seed': f'{seed}'})

    with open('../faulty.json', 'w') as f:
        json.dump(faulty_config, f, indent=4)
        f.close()

def read_time():
    with open(f'../faulty.json') as f:
        faulty_config = json.load(f)
        f.close()
    return faulty_config['time_seed']

