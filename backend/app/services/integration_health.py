import time
import uuid
from typing import Any

from ..config import settings
from ..config import settings
from .storage_service import storage_service



# MODAL_APP_NAME = "proedit-worker"
# MODAL_FUNCTION_NAME = "render_video_v1"


# Global Cache for performance
_CACHED_MODAL = None
_LAST_MODAL_CHECK = 0.0

def check_modal_lookup() -> dict[str, Any]:
    # configured = bool(settings.modal_token_id and settings.modal_token_secret)

    result: dict[str, Any] = {
        "configured": False,
        "reachable": False,
        # "app": MODAL_APP_NAME,
        # "function": MODAL_FUNCTION_NAME,
        "note": "Modal integration disabled for local hosting"
    }
    return result


def check_r2_probe(run_probe: bool) -> dict[str, Any]:
    """
    Verify R2 connectivity.
    - Summary mode: only reports config/use_r2 status.
    - Probe mode: does put/get/delete on a temporary object.
    """
    configured = bool(storage_service.use_r2 and storage_service.s3_client and storage_service.bucket)
    result: dict[str, Any] = {
        "configured": configured,
        "reachable": False,
        "bucket": getattr(storage_service, "bucket", None),
    }

    if not configured:
        result["error"] = "R2 not configured"
        return result

    if not run_probe:
        result["reachable"] = True
        return result

    client = storage_service.s3_client
    bucket = storage_service.bucket
    probe_key = f"health/probe-{uuid.uuid4().hex}.txt"
    payload = f"probe-{uuid.uuid4().hex}".encode("utf-8")

    start = time.perf_counter()
    try:
        client.put_object(Bucket=bucket, Key=probe_key, Body=payload, ContentType="text/plain")
        obj = client.get_object(Bucket=bucket, Key=probe_key)
        read_back = obj["Body"].read()
        obj["Body"].close()
        client.delete_object(Bucket=bucket, Key=probe_key)

        result["reachable"] = read_back == payload
        result["roundtrip_ms"] = int((time.perf_counter() - start) * 1000)
        if not result["reachable"]:
            result["error"] = "R2 probe payload mismatch"
        return result
    except Exception as e:
        try:
            client.delete_object(Bucket=bucket, Key=probe_key)
        except Exception:
            pass
        result["error"] = str(e)
        result["roundtrip_ms"] = int((time.perf_counter() - start) * 1000)
        return result


def get_integration_health(run_probe: bool = False) -> dict[str, Any]:
    return {
        "modal": check_modal_lookup(),
        "r2": check_r2_probe(run_probe=run_probe),
    }
