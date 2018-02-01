f = open("vvvvvvmusic.vvv", 'rb')
q = f.read()

FILE_NAMES = ['0levelcomplete.ogg','1pushingonwards.ogg','2positiveforce.ogg','3potentialforanything.ogg','4passionforexploring.ogg','5intermission.ogg','6presentingvvvvvv.ogg','7gamecomplete.ogg','8predestinedfate.ogg','9positiveforcereversed.ogg','10popularpotpourri.ogg','11pipedream.ogg','12pressurecooker.ogg','13pacedenergy.ogg','14piercingthesky.ogg']

startAt = endAt = -1
musStartAt = musEndAt = -1
currentMus = 0
while True:
    oldStartAt = startAt
    startAt = q.find("OggS", oldStartAt + 1)
    endAt = q.find("OggS", startAt + 1) - 1
    if oldStartAt >= startAt:
        break
    if endAt == -2:
        endAt = len(q) - 1
    sB = ord(q[startAt+5])
    if sB == 2:
        musStartAt = startAt
    elif sB == 4:
        musEndAt = endAt
        print "Found entire Ogg between",musStartAt,musEndAt
        print "Filename: ",FILE_NAMES[currentMus]
        f2 = open(FILE_NAMES[currentMus], 'wb')
        f2.write(q[musStartAt:musEndAt])
        f2.close()
        currentMus += 1
    #print "Found OggS at",startAt,"-",endAt