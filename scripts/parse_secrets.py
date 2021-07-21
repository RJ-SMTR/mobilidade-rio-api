import base64

"""
This script parses a .env file and returns
a secrets.yml ready for Kubernetes.
"""

env_vars = []

with open(".env") as f:
    for line in f:
        if line.startswith('#') or not line.strip():
            continue
        key, value = line.strip().split('=', 1)
        value = value if value else "\"\""
        env_vars.append({'name': key, 'value': value})

base_text = """apiVersion: v1
kind: Secret
metadata:
  name: envs
data:
"""


def encode_b64(txt: str):
    return base64.b64encode(txt.encode('ascii')).decode('ascii')


with open("secrets.yaml", "w") as f:
    f.write(base_text)
    for var in env_vars:
        f.write(f'  {var["name"]}: {encode_b64(var["value"])}\n')
