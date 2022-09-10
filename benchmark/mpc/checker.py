
import os
import json




bench_parameters = {
    "nodes": 4,
    "rate": 30000,
    "tx_size": 512,
    "faults": 0,
    "replicas": 5,
    "servers": 10,
    "duration": 50,
    "delay": 0,
    "local": False,
    "parsing": False,
    "partition": False,
    "S2f": False
}

node_parameters = {
    "consensus": {
        "max_payload_size": 32,     # digest of the transaction
        "min_block_delay": 0,
        "sync_retry_delay": 1000,
        "timeout_delay": 1000
    },
    "mempool": {
        "max_payload_size": 500000,         
        "min_block_delay": 0,
        "queue_capacity": 100000,
        "sync_retry_delay": 1000
    }
}

with open('../node_parameters.json', 'w') as f:
    json.dump(node_parameters, f, indent=4)
    f.close()


scenarios = ["S3"]

for scenario in scenarios:

    if scenario == "S1":
        replicas = [1, 5]
        rates = [10000]
        round = 1

        # replicas = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        # rates = [4000, 5000, 6000, 7000, 8000, 9000, 10000]
        # round = 20

        bench_parameters['delay'] = 0
        bench_parameters['faults'] = 0
        bench_parameters['S2f'] = False

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

    elif scenario == "S2":
        replicas = [1, 5, 10]
        rates = [10000]
        round = 20
        # replicas = [1,2,3,4,5,6]
        # rates = [20000, 30000, 40000, 50000,60000]
        # rate = 20
        # time = 16.7 Hour
        # number of f: 1-f

        # 1, 5, 10
        # 10k
        # 3, 16, 33
        bench_parameters['delay'] = 0
        bench_parameters['S2f'] = False

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

    elif scenario == "S2f":

        replicas = [1, 5, 10]
        rates = [10000]
        round = 20
        bench_parameters['delay'] = 0
        bench_parameters['S2f'] = True

        for rep in replicas:
            bench_parameters['replicas'] = rep
            faults = rep*3 + (rep-1)//3

            for f in range(faults+1):
                bench_parameters['faults'] = f
                for rat in rates:
                        bench_parameters['rate'] = rat
                        with open('../bench_parameters.json', 'w') as f:
                                json.dump(bench_parameters, f, indent=4)
                                f.close()
                        
                        for r in range(round):
                            os.system('fab faulty')
                            os.system('fab parsing')


    elif scenario == "S3":
        replicas = [1, 5, 10]
        rates = [10000]
        # delay = [10, 25, 50, 100, 250, 500, 1000, 2000, 3000, 4000, 5000]  # lower delay, timeout:5000
        delay = [10, 50, 500, 1000, 5000]
        round = 3                            
        # replicas = [3,4,5,6]
        # rates = [30000, 40000, 50000,60000]
        # delay = [3000, 4000, 5000, 6000, 7000]
        # round = 20
        # time = 44 Hour

        # 1, 5, 10
        # 10 k
        # 10 25 50 100 250 500 1000 2000 3000 4000 5000
        bench_parameters['faults'] = 0
        bench_parameters['S2f'] = False
        for rep in replicas:
            bench_parameters['replicas'] = rep
            for rat in rates:
                    bench_parameters['rate'] = rat
                    
                    for de in delay:
                        bench_parameters['delay'] = de
                        with open('../bench_parameters.json', 'w') as f:
                                json.dump(bench_parameters, f, indent=4)
                                f.close()
                        
                        for r in range(round):
                            os.system('fab timeout')
                            os.system('fab parsing')