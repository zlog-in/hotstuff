use crate::{
    consensus::{Round, CHANNEL_CAPACITY},
    error::{ConsensusError, ConsensusResult},
    messages::Block,
};
use crypto::{Digest, Hash as _};
use futures::{
    future::try_join_all,
    stream::{futures_unordered::FuturesUnordered, StreamExt as _},
};
use log::error;
use mempool::Committee as MempoolCommittee;
use std::collections::HashMap;
use store::Store;
use tokio::sync::mpsc::{channel, Receiver, Sender};

pub struct MempoolDriver {
    committee: MempoolCommittee,
    store: Store,
    tx_mempool: Sender<Vec<Digest>>,
    tx_payload_waiter: Sender<PayloadWaiterMessage>,
}

impl MempoolDriver {
    pub fn new(
        committee: MempoolCommittee,
        store: Store,
        tx_mempool: Sender<Vec<Digest>>,
        tx_loopback: Sender<Block>,
    ) -> Self {
        let (tx_payload_waiter, rx_payload_waiter) = channel(CHANNEL_CAPACITY);

        // Spawn the payload waiter.
        PayloadWaiter::spawn(store.clone(), rx_payload_waiter, tx_loopback);

        // Returns the mempool driver.
        Self {
            committee,
            store,
            tx_mempool,
            tx_payload_waiter,
        }
    }

    pub async fn verify(&mut self, block: Block) -> ConsensusResult<bool> {
        let mut missing = Vec::new();
        for x in &block.payload {
            x.verify(&self.committee)?;

            if self.store.read(x.root.to_vec()).await?.is_none() {
                missing.push(x.root.clone());
            }
        }

        if missing.is_empty() {
            return Ok(true);
        }

        self.tx_mempool
            .send(missing.clone())
            .await
            .expect("Failed to send sync message");

        self.tx_payload_waiter
            .send(PayloadWaiterMessage::Wait(missing, block))
            .await
            .expect("Failed to send message to payload waiter");

        //Ok(false)
        Ok(true)
    }

    pub async fn cleanup(&mut self, round: Round) {
        // Cleanup the payload waiter.
        self.tx_payload_waiter
            .send(PayloadWaiterMessage::Cleanup(round))
            .await
            .expect("Failed to send cleanup message");
    }
}

#[derive(Debug)]
enum PayloadWaiterMessage {
    Wait(Vec<Digest>, Block),
    Cleanup(Round),
}

struct PayloadWaiter {
    store: Store,
    rx_message: Receiver<PayloadWaiterMessage>,
    tx_loopback: Sender<Block>,
}

impl PayloadWaiter {
    pub fn spawn(
        store: Store,
        rx_message: Receiver<PayloadWaiterMessage>,
        tx_loopback: Sender<Block>,
    ) {
        tokio::spawn(async move {
            Self {
                store,
                rx_message,
                tx_loopback,
            }
            .run()
            .await;
        });
    }

    async fn waiter(
        mut missing: Vec<(Digest, Store)>,
        deliver: Block,
        mut handler: Receiver<()>,
    ) -> ConsensusResult<Option<Block>> {
        let waiting: Vec<_> = missing
            .iter_mut()
            .map(|(x, y)| y.notify_read(x.to_vec()))
            .collect();
        tokio::select! {
            result = try_join_all(waiting) => {
                result.map(|_| Some(deliver)).map_err(ConsensusError::from)
            }
            _ = handler.recv() => Ok(None),
        }
    }

    async fn run(&mut self) {
        let mut waiting = FuturesUnordered::new();
        let mut pending = HashMap::new();

        let store_copy = self.store.clone();
        loop {
            tokio::select! {
                Some(message) = self.rx_message.recv() => match message {
                    PayloadWaiterMessage::Wait(missing, block) => {
                        let block_digest = block.digest();

                        if pending.contains_key(&block_digest) {
                            continue;
                        }

                        let (tx_cancel, rx_cancel) = channel(1);
                        pending.insert(block_digest, (block.round, tx_cancel));
                        let wait_for = missing.iter().cloned().map(|x| (x, store_copy.clone())).collect();
                        let fut = Self::waiter(wait_for, block, rx_cancel);
                        waiting.push(fut);
                    },
                    PayloadWaiterMessage::Cleanup(mut round) => {
                        for (r, handler) in pending.values() {
                            if r <= &round {
                                let _ = handler.send(()).await;
                            }
                        }
                        pending.retain(|_, (r, _)| r > &mut round);
                    }
                },
                Some(result) = waiting.next() => {
                    match result {
                        Ok(Some(block)) => {
                            let _ = pending.remove(&block.digest());
                            self.tx_loopback.send(block).await.expect("Failed to send consensus message");
                        },
                        Ok(None) => (),
                        Err(e) => error!("{}", e)
                    }
                }
            }
        }
    }
}
