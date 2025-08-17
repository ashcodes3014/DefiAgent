from firebase_config import rtdb
from firebase_config import fs


def fetch_chosen_wallets():
    chosen_wallets_list = []

    rtdb_users_ref = rtdb.reference("USERS")
    users_data = rtdb_users_ref.get()

    if not users_data:
        print("No users in Realtime DB.")
        return chosen_wallets_list

    for uid, user_info in users_data.items():
        wallets = user_info.get("wallets", {})

        if not isinstance(wallets, dict):
            print(f"[ERROR] Wallets field is not a dict for user {uid}")
            continue

        for address, wallet_info in wallets.items():
            if isinstance(wallet_info, dict) and wallet_info.get("choosen", False):
                chosen_wallets_list.append({
                    "uid": uid,
                    "address": address.strip()
                })

    return chosen_wallets_list


def get_user_wallet_data(uid, address):
    wallet_ref = (
        fs.collection("USERS")
        .document(uid)
        .collection("wallets")
        .document(address)
    )

    wallet_doc = wallet_ref.get()

    if wallet_doc.exists:
        wallet_data = wallet_doc.to_dict()
        networth = wallet_data.get("networth", {})
        chains = networth.get("chains", [])

        result = {
            "uid": uid,
            "address": address,
            "chains": [
                {
                    "chain": chain_obj.get("chain"),
                    "balance": chain_obj.get("networth_usd")
                }
                for chain_obj in chains
            ]
        }
        return result


def get_all_users_wallets(data_array):
    results = []
    for item in data_array:
        uid = item["uid"]
        address = item["address"]
        result = get_user_wallet_data(uid, address)
        if(result): results.append(result)
    return results




