source /root/.cargo/env
cd /home/hotstuff/benchmark/
git restore .committee.json
git pull
#rm logs/*.log

fab local
