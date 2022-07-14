import sqlite3


db = 'results.db'
results_db = sqlite3.connect(db)

creat_scenario1_hotstuff = """CREATE TABLE IF NOT EXISTS S1Hotstuff (
                         Date text,
                         Local integer,
                         Replicas integer,
                         Faults integer,
                         Timeout integer,
                         Sync_Retry interger,
                         Duration integer,
                         Input_Rate integer,
                         TPS integer,
                         Consensus_Latency integer,
                         E2E_Latency integer
                         )
                         """
results_db.cursor().execute(creat_scenario1_hotstuff)
results_db.commit()



creat_scenario2_hotstuff = """CREATE TABLE IF NOT EXISTS S2Hotstuff (
                         Date text,
                         Local integer,
                         Replicas integer,
                         Faults integer,
                         Timeout integer,
                         Sync_Retry interger,
                         Duration integer,
                         Input_Rate integer,
                         TPS integer,
                         Consensus_Latency integer,
                         E2E_Latency integer
                         )
                         """
results_db.cursor().execute(creat_scenario2_hotstuff)
results_db.commit()
results_db.close()
