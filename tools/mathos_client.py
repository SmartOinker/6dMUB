#!/usr/bin/env python3
"""Minimal client for the Open Math OS Platform API (https://os.openmathmodel.org/v1/openapi.json).

Every platform operation is `POST /v1/{operation}` with a JSON body and a platform key (`nuc_oc_...`) as bearer
token. The key is read from the environment variable MATHOS_KEY and is never written to disk.

    export MATHOS_KEY=nuc_oc_...
    python3 mathos_client.py call account
    python3 mathos_client.py call orgs
    python3 mathos_client.py wake TEAM                      # repeats until the team's VM is ready
    python3 mathos_client.py call project_create '{"team": "TEAM", "display_name": "bridge-lean"}'
    python3 mathos_client.py call chat_create   '{"team": "TEAM", "project": "PROJECT", "title": "build"}'
    python3 mathos_client.py upload TEAM PROJECT local/file.lean path/in/repo/file.lean
    python3 mathos_client.py call chat_say '{"team": "TEAM", "project": "PROJECT", "session": "S", "text": "..."}'
    python3 mathos_client.py history TEAM PROJECT SESSION   # prints the session's records
    python3 mathos_client.py download TEAM PROJECT path/in/repo/build.log local/build.log
    python3 mathos_client.py ls TEAM PROJECT [path]

There is no "compile Lean" endpoint: a Lean build is done by asking the platform's agent in a chat and reading
back the log it writes into the project's repository.
"""
import json, os, sys, time, urllib.request, urllib.error

BASE = "https://os.openmathmodel.org/v1"


def _key():
    k = os.environ.get("MATHOS_KEY")
    if not k:
        sys.exit("set MATHOS_KEY to your platform key (nuc_oc_...)")
    return k


def _request(op, data=None, headers=None, raw=False, timeout=120):
    # A descriptive User-Agent is required: the default Python one is rejected by the CDN (error 1010).
    h = {"Authorization": "Bearer " + _key(), "User-Agent": "mathos-client/0.1", "Accept": "*/*"}
    h.update(headers or {})
    if data is None:
        data = b"{}"
    if "Content-Type" not in h:
        h["Content-Type"] = "application/json"
    req = urllib.request.Request(f"{BASE}/{op}", data=data, headers=h, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read()
            return r.status, (body if raw else json.loads(body or b"{}"))
    except urllib.error.HTTPError as e:
        body = e.read()
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, {"error": body.decode("utf-8", "replace")[:2000]}


def call(op, body=None):
    return _request(op, json.dumps(body or {}).encode())


def wake(team, tries=60, pause=10):
    for _ in range(tries):
        status, out = call("wake", {"team": team})
        print(status, json.dumps(out))
        if status == 200:
            return out
        if status != 202:
            sys.exit(1)
        time.sleep(pause)
    sys.exit("VM not ready")


def upload(team, project, local, path):
    arg = json.dumps({"team": team, "project": project, "path": path})
    with open(local, "rb") as f:
        return _request("files_upload", f.read(), {"x-nucleus-arg": arg, "Content-Type": "application/octet-stream"})


def download(team, project, path, local):
    arg = json.dumps({"team": team, "project": project, "path": path})
    status, body = _request("files_download", b"", {"x-nucleus-arg": arg}, raw=True)
    if status == 200:
        with open(local, "wb") as f:
            f.write(body)
    return status, (len(body) if status == 200 else body)


def history(team, project, session, after=None, limit=200):
    body = {"team": team, "project": project, "session": session, "limit": limit}
    if after is not None:
        body["after"] = after
    return call("session_history", body)


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    if a[0] == "call":
        out = call(a[1], json.loads(a[2]) if len(a) > 2 else None)
    elif a[0] == "wake":
        out = wake(a[1])
    elif a[0] == "upload":
        out = upload(*a[1:5])
    elif a[0] == "download":
        out = download(*a[1:5])
    elif a[0] == "history":
        out = history(*a[1:4])
    elif a[0] == "ls":
        body = {"team": a[1], "project": a[2]}
        if len(a) > 3:
            body["path"] = a[3]
        out = call("files_list", body)
    else:
        sys.exit(__doc__)
    print(json.dumps(out, indent=1) if not isinstance(out, tuple) else json.dumps(list(out), indent=1, default=str))
