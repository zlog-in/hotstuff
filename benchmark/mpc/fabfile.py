from fabric import Connection, ThreadingGroup
from fabric import task
import subprocess


@task
def benchmarking(ctx):
    hosts = ThreadingGroup('mpc-0','mpc-1','mpc-2','mpc-3','mpc-4','mpc-5','mpc-6','mpc-7','mpc-8','mpc-9')
    hosts.run('docker stop narwhal')
    hosts.run('docker start hotstuff')
    hosts.run('docker exec -t hotstuff bash ben.sh')

@task
def container(ctx):
    hosts = ThreadingGroup('mpc-0','mpc-1','mpc-2','mpc-3','mpc-4','mpc-5','mpc-6','mpc-7','mpc-8','mpc-9')
    hosts.run('rm -rf hotstuff/logs/')
    hosts.run('mkdir -p hotstuff/logs')

    hosts.put('/home/z/Sync/Study/DSN/Marc/Code/hotstuff/benchmark/mpc/ben.sh', remote='/home/zhan/hotstuff')
    hosts.run('docker stop narwhal')
    hosts.run('docker rm -f hotstuff')
    hosts.run('docker run -itd --name hotstuff -p 9000-9049:9000-9049 --mount type=bind,source=/home/zhan/hotstuff/logs,destination=/home/hotstuff/benchmark/logs image_hotstuff')
    hosts.run('docker cp index.txt hotstuff:/home/hotstuff/benchmark/')
    hosts.run('docker cp hotstuff/ben.sh hotstuff:/home/hotstuff/benchmark/')

@task
def parsing(ctx):
    subprocess.call(['bash', '../parsing.sh'])

@task
def build(ctx):
    hosts = ThreadingGroup('mpc-0','mpc-1','mpc-2','mpc-3','mpc-4','mpc-5','mpc-6','mpc-7','mpc-8','mpc-9')
    hosts.run('rm -rf hotstuff/')
    hosts.run('mkdir  hotstuff/')
    hosts.put('/home/z/Sync/Study/DSN/Marc/Code/hotstuff/benchmark/mpc/Dockerfile', remote='/home/zhan/hotstuff')
    # hosts.run('docker rm -f hotstuff')
    # hosts.run('docker rmi image_hotstuff')
    hosts.run('docker build -f /home/zhan/hotstuff/Dockerfile -t image_hotstuff .')
