cubelabels = "fblrud"
levels = ["l"+i for i in range(1,8)]
skipped = 0
for s in cubelabels:
  for l in levels:
    for v in range(1,999):
      for h in range(1,999):
        req = requests.get("http://europe.tiles.fanpic.co/749-2017-cnn/mres_{s}/{l}/{v}/{l}_{s}_{v}_{h}.jpg".format(s=s,l=l,v=v,h=h), stream=True)
        if req.status_code == 200:
          with open("{l}_{s}_{v}_{h}.jpg".format(s=s,l=l,v=v,h=h), "wb") as f:
            for chunk in req:
              _ = f.write(chunk)
          print("Done {l}_{s}_{v}_{h}.jpg".format(s=s,l=l,v=v,h=h))
        else:
          print("Skipping on {l}_{s}_{v}_{h}.jpg".format(s=s,l=l,v=v,h=h))
          skipped += 1
          break
      if skipped >= 3:
        skipped = 0
        break