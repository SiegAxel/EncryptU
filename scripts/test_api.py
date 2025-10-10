import requests
import io

API = 'http://127.0.0.1:8000'


def test_register_login_and_upload():
    u = 'testuser'
    p = 'testpass'
    # register
    r = requests.post(f"{API}/register", params={'username': u, 'password': p})
    print('register', r.status_code, r.text)
    # login to get token
    r2 = requests.post(f"{API}/login", data={'username': u, 'password': p})
    print('login', r2.status_code, r2.text)
    token = None
    if r2.status_code == 200:
        token = r2.json().get('access_token')
    headers = {'Authorization': f'Bearer {token}'} if token else None
    # upload
    f = io.BytesIO(b'hello world')
    files = {'file': ('hello.txt', f)}
    r3 = requests.post(f"{API}/upload", files=files, headers=headers)
    print('upload', r3.status_code, r3.text)
    # list files
    r4 = requests.get(f"{API}/files", headers=headers)
    print('files', r4.status_code, r4.text)
    # download first file if present
    if r4.status_code == 200 and isinstance(r4.json(), list) and len(r4.json()) > 0:
        fid = r4.json()[0]['id']
        r5 = requests.get(f"{API}/download/{fid}", headers=headers)
        print('download', r5.status_code)
        if r5.status_code == 200:
            print('downloaded bytes', len(r5.content))

if __name__ == '__main__':
    test_register_login_and_upload()
