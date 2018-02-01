#!/usr/bin/env python3
#
# http://www.pangloss.com/seidel/shake_rule.html
# Shakespeare Insult Kit
# 
# Combine one word from each of the three columns below, prefaced with "Thou":
# 
import random

Column_1 ="""artless bawdy beslubbering bootless churlish cockered
clouted craven currish dankish dissembling droning errant fawning
fobbing froward frothy gleeking goatish gorbellied impertinent
infectious jarring loggerheaded lumpish mammering mangled mewling
paunchy pribbling puking puny qualling rank reeky roguish ruttish
saucy spleeny spongy surly tottering unmuzzled vain venomed villainous
warped wayward weedy yeasty cullionly fusty caluminous wimpled
burly-boned misbegotten odiferous poisonous fishified Wart-necked""".split()
         
Column_2 = """base-court bat-fowling beef-witted beetle-headed
boil-brained clapper-clawed clay-brained common-kissing crook-pated
dismal-dreaming dizzy-eyed doghearted dread-bolted earth-vexing
elf-skinned fat-kidneyed fen-sucked flap-mouthed fly-bitten
folly-fallen fool-born full-gorged guts-griping half-faced
hasty-witted hedge-born hell-hated idle-headed ill-breeding
ill-nurtured knotty-pated milk-livered motley-minded onion-eyed
plume-plucked pottle-deep pox-marked reeling-ripe rough-hewn
rude-growing rump-fed shard-borne sheep-biting spur-galled
swag-bellied tardy-gaited tickle-brained toad-spotted unchin-snouted
weather-bitten whoreson malmsey-nosed rampallian lily-livered
scurvy-valiant brazen-faced unwash'd bunch-back'd leaden-footed
muddy-mettled pigeon-liver'd scale-sided""".split()

Column_3 = """apple-john baggage barnacle bladder boar-pig bugbear
bum-bailey canker-blossom clack-dish clotpole coxcomb codpiece
death-token dewberry flap-dragon flax-wench flirt-gill foot-licker
fustilarian giglet gudgeon haggard harpy hedge-pig horn-beast
hugger-mugger joithead lewdster lout maggot-pie malt-worm mammet
measle minnow miscreant moldwarp mumble-news nut-hook pigeon-egg
pignut puttock pumpion ratsbane scut skainsmate strumpet varlot vassal
whey-face wagtail knave blind-worm popinjay scullian jolt-head
malcontent devil-monk toad rascal Basket-Cockle""".split()

print("Thou %s %s %s!"%((random.choice(Column_1),
                         random.choice(Column_2),
                         random.choice(Column_3))))
