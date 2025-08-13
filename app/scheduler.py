import time
import schedule
from firebase_config import fs
from dataFetcher import get_coin_features
from llm_agent import get_llm_action,get_name
from notifier import send_fcm_notification
from fetch import fetch_users_wallet_chain_fcm

def check_and_notify():
    users_data = fetch_users_wallet_chain_fcm()
    print(f"\n[CHECK] Checking {len(users_data)} users...")

    for user in users_data:
        uid = user["uid"]
        fcm_token = user["fcm_token"]
        wallets = user["wallets"]

        changed_coins = []
        updates = {}

        for wallet in wallets:
            wallet_address = wallet["address"]
            chains = wallet["chains"] 

            for chain in chains:
                print(f"→ Processing {wallet_address} ({chain}) for user {uid}")

                current_status = "Hold" 
                chain_name = get_name(chain)
                result = get_coin_features(chain_name)

                if not result["success"]:
                    print(f"Failed to fetch features for {wallet_address}: {result['error']}")
                    continue

                features = result["data"]
                print(result['data'])
                llm_output = get_llm_action(features)

                if not llm_output or "action" not in llm_output or "reason" not in llm_output:
                    print(f"[ERROR] Invalid LLM output for {wallet_address}")
                    continue

                suggested_action = llm_output["action"]

                if suggested_action != current_status:
                    print(f"{wallet_address} ->  {current_status} to {suggested_action}")
                    changed_coins.append({
                        "coin_id": wallet_address.upper(),
                        "chain": chain,
                        "old": current_status,
                        "new": suggested_action,
                        "reason": llm_output["reason"]
                    })
                    updates[wallet_address] = suggested_action
                else:
                    print(f"[INFO] No action change for {wallet_address} ({suggested_action}) on {chain}")

        if changed_coins:
            title = "Portfolio Signal Changed"
            body_lines = [
                 f"{coin['chain'].upper()}: Status changed from {coin['old']} to {coin['new']} \n Reason: {coin['reason']}"
                    for coin in changed_coins
            ]
            body = "\n".join(body_lines)

            send_fcm_notification(fcm_token, uid, title, body)

            for wallet_address, new_status in updates.items():
                wallet_ref = fs.collection("USERS").document(uid).collection("wallets").document(wallet_address)
                wallet_ref.set({"status": new_status}, merge=True)

def run_scheduler():
    schedule.every(1).minutes.do(check_and_notify)
    print("[SCHEDULER] Started. Running every 1 minute...")
    while True:
        schedule.run_pending()
        time.sleep(10)
