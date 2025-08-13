import firebase_admin
from firebase_admin import messaging, credentials

if not firebase_admin._apps:
    cred = credentials.Certificate("firebase.json")
    firebase_admin.initialize_app(cred)

def send_fcm_notification(fcm_token, user_id, title, body):
    try:
        if not fcm_token:
            print(f"No FCM token for user {user_id}. Notification skipped.")
            return

        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            token=fcm_token
        )
        print("message\n")
        print(message)
        response = messaging.send(message)
        print(f"Notification sent to {user_id}: {response}")

    except Exception as e:
        print(f"[ERROR] Failed to send FCM notification to {user_id}: {str(e)}")
