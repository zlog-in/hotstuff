
import os
import json



bench_parameters = {
    "nodes": 4,
    "rate": 30000,
    "tx_size": 512,
    "faults": 0,
    "duration": 100,
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



replicas = [1, 2, 3, 4, 5]

rates = [40000, 50000, 60000]

round = 20


# for i in range(10):
#     os.system('fab timeout')
#     print("One round finished")
#     os.system('fab parsing')

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
