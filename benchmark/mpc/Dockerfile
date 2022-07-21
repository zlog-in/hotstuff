FROM ubuntu:latest

RUN apt update && apt install git vim clang tmux curl python3-pip fabric -y  && curl https://sh.rustup.rs -sSf | bash -s -- -y && echo 'source $HOME/.cargo/env' >> $HOME/.bashrc && cd /home/ && git clone https://github.com/zlog-in/hotstuff/ && cd /home/hotstuff/benchmark/ && git checkout faulty && pip install -r requirements.txt

WORKDIR /home/hotstuff/benchmark
