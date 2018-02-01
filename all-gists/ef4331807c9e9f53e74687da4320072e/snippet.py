from time import *
levelcomplete1 = 'Complete ✅ good job!'
levelcomplete2 = 'Complete ✅ not so good job!'
name = input('enter name : ')
start = input('do you want to play in english or swedish? eng/swe : ')
if start == 'swe' :
	print('LONDONRESAN EPISOD 1')
	print('Du är i ett rumm. Du sitter och funderar på om du ska acceptera din inbjudan till en resa till london. vad gör du')
	ett = input('1 : accepterar. 2 : tackar nej på ett artigt sätt.')
	if ett == '1' :
		print('Du börgar skriva i brevet.')
		print(name + ' -Hejsan jag följer gärna med till london')
		sleep(1)
		print(name + '-Så nu är det bara att skicka brevet till dem och få biljetterna')
		sleep(0.5)
		print('du går till dörren och lägger brevet i brevlådan hos din granne som skickade brevet.')
		sleep(0.01)
		print(name + ' - *pust* Då var det gjort nu kan jag...')
		två = input('1 : Hoppa i studsmattan. 2 : ha party')
		if två == '2' :
			print('Du går hem och börjar skriva inbjudningar för din fest.')
			sleep(20)
			print(name + ' -hos ' + name + ' klockan tolv. Så då var det klart dags att dela ut dem!')
			sleep(1)
			print('Du går utanför dörren och där möter du en...')
			print(levelcomplete1)
		else:
			print('Du går och börjar hoppa i din studsmatta')
			sleep(1)
			print('Då ser Gustav dig')
			sleep(0.5)
			print('Gustav -Hallå där får jag vara med och hoppa?')
			sleep(3)
			tre = input('1 : javisst får du vara med. 2 : nix det få du inte')
			if tre == '1' :
				print(name + ' -Javisst får du vara med!')
				sleep(1)
				print('och så hoppar ni tillsamans tills ni dör.')
				print(levelcomplete1)
			else:
				print(name + ' -nix')
				print('Gustav -Ok. Men du får då inte följa med till london!')
				print(levelcomplete2)
	else:
			print(name + ' -Nej tyvär jag kan inte komma meed. Så då var det skrivet.')
			print('Du går till din granne som gav dig din inbjudan och ger den till han.')
			sleep(1)
			print('Gustav -Så du tackar nej till min svindyra inbjudan!!!')
			sleep(0.5)
			print(name + ' -Men jag har faktisk inge..')
			sleep(0.00000001)
			print('Gustav -Ingen vadå')
			sleep(0.5)
			print(name + ' -Tid!')
			sleep(0.5)
			print('Du stryps och faller ned på marken!')
			print(levelcomplete2)
else:
	print('Comming soon!')
from time import *
good = 'Complete ✅ good job'
bad = 'complete ✅ not so good job'
lan = input('Do you want to play in english or swedish? eng/swe ')
if lan == 'swe' :
	print('LONDONRESAN EPISOD 2')
	endi = input('Fick du slutet som slutade med ... ? j/n ')
	if endi == 'j' :
		print('...Främling')
		sleep(0.5)
		print('Främlingen -Hit med stålarna!')
		sleep(0.5)
		print('Främlingen -Om du har några alltså.')
		ett = input('1 : Jag har inga stålar. Jag lovar! 2 : Ok här')
		if ett == '1' :
			print(name + ' -Jag har inga stålar. Jag lovar!')
			sleep(1)
			print('Främlingen -De ska vi minnsan kolla igenom!')
			sleep(0.5)
			print('Främlingen skakar dig upp och ned , upp och ned om och om igen')
			sleep(5)
			print('Främlingen -Ok det är sant. *suck*')
			sleep(0.5)
			print('Främlingen går iväg från dig')
			print('Och du...')
			två = input('1 : Går hem. 2 : Går till din granne Gustav')
			if två == '1' :
				print('Du springer hem och du...')
				tre = input('1 : ringer 112. 2 : börjar packa')
				if tre == '1' :
					print('Du ringer 112')
					print('Rrring Rrring')
					print(name + ' -Hej jag såg en främling som försökte ta mina pengar på sköndalsvägen 129')
					sleep(6)
					print('Du inser att du är försenad och inte kommer hinna med planet!')
					print(bad)
				else:
					print('Du springer och börjar packa. Men frågan är om du kommer hinna med planet...')
					print(good)
			else:
					print('Du går till din granne Gustav och ser en lapp där det står : Åker på en resa till London kommer hem snart.')
					sleep(1)
					print('Då inser du att du kommer att missa flyget.')
					print(bad)
		else:
			print('Främlingen tar fram en kniv och mördar dig')
			print(bad)
	else:
		print(bad)
else:
	print('Comming soon')
	print(bad)
good = 'YOU DID IT'
bad = 'GAME OVER'
from time import *
from calendar import *
l = input('Do you want to play in english or swedish? eng/swe ')
if l == 'swe' : 
	ett = input('Slutade det inte med et... j/n ')
	if ett == 'j' :	
		print('Du hinner precis med planet och sätter dig vid Gustav')
		sleep(1)
		print('Gustav -Tur att du hann med planet. Det var verkligen sista sekunden')
		sleep(0.5)
		print(name + ' -Japp')
		print('Ni åker i åtta timmar. Men det är för mycket tid så vi spolar till 10 sekunder.')
		sleep(10)
		print('Kaptenen -Nu så landar vi i London spänn fast er. Now is we landing in london please fasten your security belt.')
		sleep(7)
		print(name + ' -Vi landar i london så spänn fast dig nu Gustav!')
		sleep(3)
		print('Gustav -Okidoki')
		sleep(1)
		print('Gustav -Ska inte du spänna fast dig då ' + name + ' ?')
		två = input('1 : [Spänn fast dig] 2 : Det har jag gjort redan.')
		if två == '1' :
			print('Du spänner fast dig *klick*')
			sleep(1)
			print('Kaptenen -Välkommna till London vi landade klockan 17:17.')
			print(good)
		else:
			print('Du tänker spänna fast dig innan Gustav ser att du inte har gjort det. Men det är för sent ni har krockat!') 
			print(bad)
	else:
		print(bad)	
else:
	print('Comming soon')
	print(bad)
from time import sleep
lang = input('eng/swe')
if lang == 'swe' :
	print('Eftertexter')
else:
	print('Credits')
print('LONDONRESAN story/berättelse : khhs. programming/programmering : khhs. programming langue/programeringsspråk : Python. app publicer/app uppläggare : mikael and/och khhs. AN KHHS🆎 CREATED APP')
print('ps:the developer whas 9 years when the game was publiched.')
print('comment from khhs : its my dad that takes care of the app.')