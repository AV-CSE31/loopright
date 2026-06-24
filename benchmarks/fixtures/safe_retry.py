class TransientError(Exception):
    pass


def upload_with_budget(client, payload, max_attempts):
    for attempt in range(1, max_attempts + 1):
        try:
            return client.upload(payload)
        except TransientError:
            if attempt == max_attempts:
                raise
