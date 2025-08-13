from firebase_config import rtdb, fs

def fetch_users_wallet_chain_fcm():
    final_data = []

    rtdb_users_ref = rtdb.reference("USERS")
    users_data = rtdb_users_ref.get()

    if not users_data:
        print("No users in Realtime DB.")
        return final_data

    for uid, user_info in users_data.items():
        username = user_info.get("name", uid)
        wallets = user_info.get("wallets", {})

        chosen_wallets = []
        if isinstance(wallets, dict):
            for address, wallet_info in wallets.items():
                if wallet_info.get("choosen", False):
                    chosen_wallets.append(address)
        else:
            print(f"[ERROR] Wallets field is not a dict for user {uid}")
            continue

        if not chosen_wallets:
            print(f"[SKIP] No chosen wallet for user {uid}")
            continue

        fs_user_ref = fs.collection("USERS").document(uid)
        fs_user_doc = fs_user_ref.get()

        if not fs_user_doc.exists:
            print(f"[Firestore] User {uid} not found")
            continue

        fs_user_data = fs_user_doc.to_dict()
        fcm_token = fs_user_data.get("fcmToken")
        if not fcm_token:
            print(f"[SKIP] No FCM token for user {uid}")
            continue

        wallet_data_list = []

        for address in chosen_wallets:
            wallet_doc_ref = fs_user_ref.collection("wallets").document(address)
            wallet_doc = wallet_doc_ref.get()

            if wallet_doc.exists:
                wallet_data = wallet_doc.to_dict()
                chain_data = wallet_data.get("chain", [])

                if isinstance(chain_data, str):
                    chain_data = [chain_data]
                elif not isinstance(chain_data, list):
                    print(f"[WARN] Invalid chain format for wallet {address} of user {uid}")
                    chain_data = []

                wallet_data_list.append({
                    "address": address,
                    "chains": chain_data
                })
            else:
                print(f"[Firestore] Wallet {address} not found under user {uid}")

        if wallet_data_list:
            final_data.append({
                "uid": uid,
                "username": username,
                "fcm_token": fcm_token,
                "wallets": wallet_data_list
            })

    return final_data
