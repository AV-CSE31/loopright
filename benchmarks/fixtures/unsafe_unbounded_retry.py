import time


def upload_forever(client, payload):
    while True:
        try:
            return client.upload(payload)
        except Exception:
            time.sleep(1)
