cd ../logs/

rm *.json

scp mpc-0:/home/zhan/hotstuff/logs/*.json ./
scp mpc-1:/home/zhan/hotstuff/logs/*.json ./
scp mpc-2:/home/zhan/hotstuff/logs/*.json ./
scp mpc-3:/home/zhan/hotstuff/logs/*.json ./
scp mpc-4:/home/zhan/hotstuff/logs/*.json ./
scp mpc-5:/home/zhan/hotstuff/logs/*.json ./
scp mpc-6:/home/zhan/hotstuff/logs/*.json ./
scp mpc-7:/home/zhan/hotstuff/logs/*.json ./
scp mpc-8:/home/zhan/hotstuff/logs/*.json ./
scp mpc-9:/home/zhan/hotstuff/logs/*.json ./

fab summary