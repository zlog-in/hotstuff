cd ../logs/
rm *.log
echo $PWD
scp mpc-0:/home/zhan/hotstuff/logs/*.log ./
scp mpc-1:/home/zhan/hotstuff/logs/*.log ./
scp mpc-2:/home/zhan/hotstuff/logs/*.log ./
scp mpc-3:/home/zhan/hotstuff/logs/*.log ./
scp mpc-4:/home/zhan/hotstuff/logs/*.log ./
scp mpc-5:/home/zhan/hotstuff/logs/*.log ./
scp mpc-6:/home/zhan/hotstuff/logs/*.log ./
scp mpc-7:/home/zhan/hotstuff/logs/*.log ./
scp mpc-8:/home/zhan/hotstuff/logs/*.log ./
scp mpc-9:/home/zhan/hotstuff/logs/*.log ./
cd ../
fab logs 
