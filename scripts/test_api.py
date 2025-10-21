import io
import os
import time
import uuid

import requests

API = os.getenv('API_URL', 'http://127.0.0.1:8000')


def _wait_for_api(timeout: float = 15.0) -> None:
    """Poll the API status endpoint until it responds or timeout expires."""
    deadline = time.time() + timeout
    status_url = f"{API}/status"

    while time.time() < deadline:
        try:
            response = requests.get(status_url, timeout=2)
            if response.status_code == 200:
                return
        except requests.RequestException:
            pass
        time.sleep(0.5)

    raise TimeoutError(f"API at {status_url} did not become ready within {timeout} seconds")


def test_register_login_and_upload():
    _wait_for_api()

    email = f"testuser_{uuid.uuid4().hex[:8]}@example.com"
    password = "testpass123!"
    name = "Test User"

    # register
    r = requests.post(
        f"{API}/register",
        json={"name": name, "email": email, "password": password},
        timeout=5,
    )
    assert r.status_code == 201, f"Register failed: {r.status_code} {r.text}"

    # login to get token
    r2 = requests.post(
        f"{API}/login",
        data={"username": email, "password": password},
        timeout=5,
    )
    assert r2.status_code == 200, f"Login failed: {r2.status_code} {r2.text}"
    token = r2.json().get('access_token')
    assert token, "Login did not return an access token"

    headers = {'Authorization': f'Bearer {token}'}

    # upload
    f = io.BytesIO(b'hello world')
    files = {'file': ('hello.txt', f, 'text/plain')}
    r3 = requests.post(f"{API}/upload", files=files, headers=headers, timeout=5)
    assert r3.status_code == 200, f"Upload failed: {r3.status_code} {r3.text}"
    file_id = r3.json().get('id')
    assert file_id is not None, "Upload response did not include file ID"

    # list files
    r4 = requests.get(f"{API}/files", headers=headers, timeout=5)
    assert r4.status_code == 200, f"List files failed: {r4.status_code} {r4.text}"
    payload = r4.json()
    assert isinstance(payload, list) and any(item['id'] == file_id for item in payload), "Uploaded file missing from listing"

    # download first file if present
    r5 = requests.get(f"{API}/download/{file_id}", headers=headers, timeout=5)
    assert r5.status_code == 200, f"Download failed: {r5.status_code} {r5.text}"
    assert r5.content == b'hello world', "Downloaded file content mismatch"


if __name__ == '__main__':
    test_register_login_and_upload()
