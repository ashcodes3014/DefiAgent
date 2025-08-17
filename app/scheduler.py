from firebase_config import fs
from dataFetcher import get_coin_features
from llm_agent import get_llm_action
import time
from datetime import datetime

symbol_to_id = {
    "eth": "ethereum",
    "bsc": "binancecoin",
    "avalanche": "avalanche-2",
    "polygon": "matic-network",
    "arbitrum": "arbitrum",
}

def process_user(user: dict):
    uid = user["uid"]
    address = user["address"]
    chains = user.get("chains", [])

    results = {"Updates": {}}

    for chain_obj in chains:
        chain_name = chain_obj.get("chain")
        balance = chain_obj.get("balance", 0)

        results["Updates"].setdefault(chain_name, {})

        chain_names = symbol_to_id[chain_name]

        features = get_coin_features(chain_names)
        if not features["success"]:
            results["Updates"][chain_name] = {
                "action": "Hold",
                "reason": f"Data fetch failed: {features['error']}",
                "balance": balance
            }
            continue

        params = features['data']
        params['balanceUSD'] = balance

        action_obj = get_llm_action(features["data"])
        results["Updates"][chain_name] = {
            "action": action_obj.get("action", "Hold"),
            "reason": action_obj.get("reason", "No data"),
            "balance": balance
        }

        time.sleep(5)

    results['Updates']['last_updated'] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    fs.collection("USERS").document(uid) \
        .collection("wallets").document(address) \
        .set(results, merge=True)

    return results
