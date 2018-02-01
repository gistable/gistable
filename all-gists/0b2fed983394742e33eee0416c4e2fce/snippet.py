import io, re, requests, sys, time, zipfile

def get_device(token):
  r = get("/api/v1/user/get", token)
  device = r.json()["user"]["devices"]
  print("Device: " + device, file = sys.stderr)
  return device

def list_presences(token, device):
  r = get("/v4/presence/{0}/latest".format(device), token)
  presences = [ presence["id"] for presence in r.json()["navigation_data"] ]
  print("Presences: {0}".format(len(presences)), file = sys.stderr)
  return presences

def download_presence(token, id):
  time.sleep(1)
  r = get("/api/v1/presence/{0}/download".format(id), token, True)
  z = zipfile.ZipFile(io.BytesIO(r.content))
  f = next(name for name in z.namelist() if re.match("device-[^-]+-presence-[\d\-\.]+\.csv", name))
  print("Presence: {0} -> {1}".format(id, f), file = sys.stderr)
  data = [ line.decode().replace("\n", "") for line in z.open(f, "rU") ]
  z.close()
  return data

def get(path, token, stream = False):
  r = requests.get("https://api-qs.emfit.com" + path, params = { "remember_token" : token }, stream = stream)
  r.raise_for_status()
  return r

def merge(records):
  assert len(records) > 1
  merged = records[0]
  for record in records[1:]:
    merged.append(record[1])
  return merged

token = "xxx"
device = get_device(token)
presences = list_presences(token, device)
records = [ download_presence(token, presence) for presence in presences ]
print("\n".join(merge(records)))
