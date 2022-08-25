
import os
import json




bench_parameters = {
    "nodes": 4,
    "rate": 30000,
    "tx_size": 512,
    "faults": 0,
    "replicas": 5,
    "servers": 10,
    "duration": 20,
    "delay": 0,
    "local": False,
    "parsing": False,
    "partition": False
}

node_parameters = {
    "consensus": {
        "max_payload_size": 2048,
        "min_block_delay": 1000,
        "sync_retry_delay": 10000,
        "timeout_delay": 10000
    },
    "mempool": {
        "max_payload_size": 2048,
        "min_block_delay": 1000,
        "queue_capacity": 100000,
        "sync_retry_delay": 10000
    }
}

with open('../node_parameters.json', 'w') as f:
    json.dump(node_parameters, f, indent=4)
    f.close()


scenario = "S1"


if scenario == "S1":
    replicas = [10]
    rates = [2500]
    round = 2
    bench_parameters['delay'] = 0
    bench_parameters['faults'] = 0

    # replicas = [1,2,3,4,5,6]
    # rates = [20000, 30000, 40000, 50000,60000]
    # rate = 20
    # time = 16.7 Hour

    for rep in replicas:
        bench_parameters['replicas'] = rep
        for rat in rates:
            bench_parameters['rate'] = rat
          
            with open('../bench_parameters.json', 'w') as f:
                    json.dump(bench_parameters, f, indent=4)
                    f.close()
            for r in range(round):
                os.system('fab faulty')
                os.system('fab parsing')

if scenario == "S2":
    replicas = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    rates = [500, 1000, 1500, 2000, 2500, 3000, 3500, 4000]
    round = 20
    # replicas = [1,2,3,4,5,6]
    # rates = [20000, 30000, 40000, 50000,60000]
    # rate = 20
    # time = 16.7 Hour
    # number of f: 1-f
    bench_parameters['delay'] = 0

    for rep in replicas:
        bench_parameters['replicas'] = rep
        bench_parameters['faults'] = rep*3 + (rep-1)//3
        
        for rat in rates:
                bench_parameters['rate'] = rat
                with open('../bench_parameters.json', 'w') as f:
                        json.dump(bench_parameters, f, indent=4)
                        f.close()
                
                for r in range(round):
                    os.system('fab faulty')
                    os.system('fab parsing')

if scenario == "S3":
    replicas = [1, 2, 3, 4, 5]
    rates = [20000, 30000, 40000, 50000]
    delay = [3000, 4000, 5000, 6000, 7000]  # lower delay, timeout:5000
    round = 20                              
    # replicas = [3,4,5,6]
    # rates = [30000, 40000, 50000,60000]
    # delay = [3000, 4000, 5000, 6000, 7000]
    # round = 20
    # time = 44 Hour

    for rep in replicas:
        bench_parameters['replicas'] = rep
        bench_parameters['faults'] = 0
        
        for rat in rates:
                bench_parameters['rate'] = rat
                
                for da in delay:
                    bench_parameters['delay'] = da
                    with open('../bench_parameters.json', 'w') as f:
                            json.dump(bench_parameters, f, indent=4)
                            f.close()
                    
                    for r in range(round):
                        os.system('fab timeout')
                        os.system('fab parsing')