from fabric import task

from benchmark.local import LocalBench
from benchmark.logs import ParseError, LogParser
from benchmark.utils import Print
from benchmark.plot import Ploter, PlotError
from aws.instance import InstanceManager
from aws.remote import Bench, BenchError
import json


@task
def local(ctx):
    ''' Run benchmarks on localhost '''
    bench_params = {
        'nodes': 4,
        'rate': 30_000,
        'tx_size': 512,
        'faults': 0,
        'duration': 60,
        'local': 0,
        'servers': 10,
    }
    node_params = {
        'consensus': {
            'timeout_delay': 5_000,
            'sync_retry_delay': 25_000,
            'max_payload_size': 500,
            'min_block_delay': 0
        },
        'mempool': {
            'queue_capacity': 20_000,
            'sync_retry_delay': 500_000,
            'max_payload_size': 20_000,
            'min_block_delay': 0
        }
    }
    try:

        with open('bench_parameters.json') as f:
            bench_parameters = json.load(f)
            f.close()
        print(type(bench_parameters))
        print(bench_parameters)
        with open('node_parameters.json') as f:
            node_parameters = json.load(f)
            f.close()
        print(node_parameters)

       
        local = bench_parameters['local'] 

        if local == True:
            ret = LocalBench(bench_parameters, node_parameters).run(debug=False).result()
            Print.info('Parsing logs...')
            print(ret)
        if local == False:
            ret = LocalBench(bench_parameters, node_parameters).run(debug=False)
            print("Parsing logs locally")
    except BenchError as e:
        Print.error(e)


@task
def create(ctx, nodes=2):
    ''' Create a testbed'''
    try:
        InstanceManager.make().create_instances(nodes)
    except BenchError as e:
        Print.error(e)


@task
def destroy(ctx):
    ''' Destroy the testbed '''
    try:
        InstanceManager.make().terminate_instances()
    except BenchError as e:
        Print.error(e)


@task
def start(ctx, max=2):
    ''' Start at most `max` machines per data center '''
    try:
        InstanceManager.make().start_instances(max)
    except BenchError as e:
        Print.error(e)


@task
def stop(ctx):
    ''' Stop all machines '''
    try:
        InstanceManager.make().stop_instances()
    except BenchError as e:
        Print.error(e)


@task
def info(ctx):
    ''' Display connect information about all the available machines '''
    try:
        InstanceManager.make().print_info()
    except BenchError as e:
        Print.error(e)


@task
def install(ctx):
    ''' Install HotStuff on all machines '''
    try:
        Bench(ctx).install()
    except BenchError as e:
        Print.error(e)


@task
def remote(ctx):
    ''' Run benchmarks on AWS '''
    bench_params = {
        'nodes': [10, 20],
        'rate': [20_000, 50_000],
        'tx_size': 512,
        'faults': 0,
        'duration': 300,
        'runs': 2,
    }
    node_params = {
        'consensus': {
            'timeout_delay': 30_000,
            'sync_retry_delay': 100_000,
            'max_payload_size': 1_000,
            'min_block_delay': 100
        },
        'mempool': {
            'queue_capacity': 500_000,
            'sync_retry_delay': 100_000,
            'max_payload_size': 500_000,
            'min_block_delay': 100
        }
    }
    try:
        Bench(ctx).run(bench_params, node_params, debug=False)
    except BenchError as e:
        Print.error(e)


@task
def plot(ctx):
    ''' Plot performance using the logs generated by "fab remote" '''
    plot_params = {
        'nodes': [10, 20],
        'tx_size': 512,
        'faults': [0],
        'max_latency': [2_000, 5_000]
    }
    try:
        Ploter.plot(plot_params)
    except PlotError as e:
        Print.error(BenchError('Failed to plot performance', e))


@task
def kill(ctx):
    ''' Stop any HotStuff execution on all machines '''
    try:
        Bench(ctx).kill()
    except BenchError as e:
        Print.error(e)


@task
def logs(ctx):
    ''' Print a summary of the logs '''
    try:
        print(LogParser.process('./logs').result())
    except ParseError as e:
        Print.error(BenchError('Failed to parse logs', e))
