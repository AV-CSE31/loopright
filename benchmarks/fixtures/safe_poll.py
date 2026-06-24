import time


def poll_job(get_status, job_id, max_polls):
    for poll_number in range(1, max_polls + 1):
        status = get_status(job_id)
        if status == "completed":
            return status
        if status in {"failed", "cancelled"}:
            raise RuntimeError(status)
        if poll_number < max_polls:
            time.sleep(1)
    raise TimeoutError("poll budget exhausted")
