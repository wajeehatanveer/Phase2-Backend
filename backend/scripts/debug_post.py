import json, urllib.request, urllib.error

try:
    data = json.dumps({"user_id":"test_user_123"}).encode()
    req = urllib.request.Request("http://127.0.0.1:8000/auth/login", data=data, headers={"Content-Type":"application/json"})
    resp = urllib.request.urlopen(req)
    token = json.load(resp)["access_token"]
    print("TOKEN", token[:50])

    task = {"title":"CLI Test","description":"desc","priority":"medium","tags":["x"]}
    data = json.dumps(task).encode()
    req2 = urllib.request.Request("http://127.0.0.1:8000/api/test_user_123/tasks", data=data, headers={"Content-Type":"application/json","Authorization":f"Bearer {token}"})
    try:
        resp2 = urllib.request.urlopen(req2)
        print("STATUS", resp2.getcode())
        print(resp2.read().decode())
    except urllib.error.HTTPError as e:
        print("ERROR", e.code)
        try:
            print(e.read().decode())
        except Exception:
            print('No body')
except Exception as e:
    print('Top-level error', repr(e))
