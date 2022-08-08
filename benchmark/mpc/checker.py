
import os
import json
from time import sleep



bench_parameters = {
    "nodes": 4,
    "rate": 30000,
    "tx_size": 512,
    "faults": 0,
    "duration": 20,
    "delay": 0,
    "local": False,
    "parsing": False,
    "servers": 10,
    "replicas": 5
}

node_parameters = {
    "consensus": {
        "max_payload_size": 5000,
        "min_block_delay": 100,
        "sync_retry_delay": 10000,
        "timeout_delay": 5000
    },
    "mempool": {
        "max_payload_size": 500000,
        "min_block_delay": 100,
        "queue_capacity": 100000,
        "sync_retry_delay": 10000
    }
}

with open('../node_parameters.json', 'w') as f:
    json.dump(node_parameters, f, indent=4)
    f.close()


scenario = "S3"


if scenario == "S1":
    replicas = [1,2,3,4,5,6,7,8,9,10]

    rates = [20000,30000,40000,50000, 60000, 70000, 80000, 90000, 100000]

    round = 10

    for rep in replicas:
        bench_parameters['replicas'] = rep
        for rat in rates:
            bench_parameters['rate'] = rat
            with open('../bench_parameters.json', 'w') as f:
                    json.dump(bench_parameters, f, indent=4)
                    f.close()
            for r in range(round):
                os.system('fab timeout')
                os.system('fab parsing')

if scenario == "S2":
    replicas = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    rates = [20000,30000, 40000, 50000, 60000, 70000, 80000, 90000, 100000]
    round = 10
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
    replicas = [1, 2]
    rates = [20000,30000]
    delay = [1000,2000]
    round = 2

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