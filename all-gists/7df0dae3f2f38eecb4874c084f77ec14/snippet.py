import os

cows = os.listdir('/usr/share/cowsay/cows')

base = r"""
@commands.command(aliases=['{0}'])
async def {1}say(self, *, txt:str):
  msg = await self.do_cowsay(txt, '{0}')
  await self.bot.say("```\n"+msg[:1992]+"```")
"""

for cow in cows:
  cow = cow[:-4]
  print(base.format(cow, cow.replace('-', '')))

@commands.command(aliases=['daemon'])
async def daemonsay(self, *, txt:str):
  msg = await self.do_cowsay(txt, 'daemon')
  await self.bot.say("```\n"+msg[:1992]+"```")


@commands.command(aliases=['pony'])
async def ponysay(self, *, txt:str):
  msg = await self.do_cowsay(txt, 'unipony-smaller')
  await self.bot.say("```\n"+msg[:1992]+"```")


@commands.command(aliases=['gnu'])
async def gnusay(self, *, txt:str):
  msg = await self.do_cowsay(txt, 'gnu')
  await self.bot.say("```\n"+msg[:1992]+"```")


@commands.command(aliases=['flamingsheep'])
async def flamingsheepsay(self, *, txt:str):
  msg = await self.do_cowsay(txt, 'flaming-sheep')
  await self.bot.say("```\n"+msg[:1992]+"```")


@commands.command(aliases=['dragon'])
async def dragonsay(self, *, txt:str):
  msg = await self.do_cowsay(txt, 'dragon')
  await self.bot.say("```\n"+msg[:1992]+"```")


@commands.command(aliases=['largepony', 'largeponysay', 'bigpony'])
async def bigponysay(self, *, txt:str):
  msg = await self.do_cowsay(txt, 'pony')
  await self.bot.say("```\n"+msg[:1992]+"```")


@commands.command(aliases=['smallpony'])
async def smallponyersay(self, *, txt:str):
  msg = await self.do_cowsay(txt, 'pony-smaller')
  await self.bot.say("```\n"+msg[:1992]+"```")


@commands.command(aliases=['turkey'])
async def turkeysay(self, *, txt:str):
  msg = await self.do_cowsay(txt, 'turkey')
  await self.bot.say("```\n"+msg[:1992]+"```")


@commands.command(aliases=['apt'])
async def aptsay(self, *, txt:str):
  msg = await self.do_cowsay(txt, 'apt')
  await self.bot.say("```\n"+msg[:1992]+"```")


@commands.command(aliases=['cower'])
async def cowersay(self, *, txt:str):
  msg = await self.do_cowsay(txt, 'cower')
  await self.bot.say("```\n"+msg[:1992]+"```")


@commands.command(aliases=['dino'])
async def dinosay(self, *, txt:str):
  msg = await self.do_cowsay(txt, 'stegosaurus')
  await self.bot.say("```\n"+msg[:1992]+"```")


@commands.command(aliases=['moofasa'])
async def moofasasay(self, *, txt:str):
  msg = await self.do_cowsay(txt, 'moofasa')
  await self.bot.say("```\n"+msg[:1992]+"```")


@commands.command(aliases=['sodomized-sheep'])
async def sodomizedsheepsay(self, *, txt:str):
  msg = await self.do_cowsay(txt, 'sodomized-sheep')
  await self.bot.say("```\n"+msg[:1992]+"```")


@commands.command(aliases=['turtle'])
async def turtlesay(self, *, txt:str):
  msg = await self.do_cowsay(txt, 'turtle')
  await self.bot.say("```\n"+msg[:1992]+"```")


@commands.command(aliases=['meow'])
async def meowsay(self, *, txt:str):
  msg = await self.do_cowsay(txt, 'meow')
  await self.bot.say("```\n"+msg[:1992]+"```")


@commands.command(aliases=['vader-koala'])
async def vaderkoalasay(self, *, txt:str):
  msg = await self.do_cowsay(txt, 'vader-koala')
  await self.bot.say("```\n"+msg[:1992]+"```")


@commands.command(aliases=['stimpy'])
async def stimpysay(self, *, txt:str):
  msg = await self.do_cowsay(txt, 'stimpy')
  await self.bot.say("```\n"+msg[:1992]+"```")


@commands.command(aliases=['dragoncow', 'dragonandcow'])
async def dragoncowsay(self, *, txt:str):
  msg = await self.do_cowsay(txt, 'dragon-and-cow')
  await self.bot.say("```\n"+msg[:1992]+"```")


@commands.command(aliases=['bong'])
async def bongsay(self, *, txt:str):
  msg = await self.do_cowsay(txt, 'bong')
  await self.bot.say("```\n"+msg[:1992]+"```")


@commands.command(aliases=['koala'])
async def koalasay(self, *, txt:str):
  msg = await self.do_cowsay(txt, 'koala')
  await self.bot.say("```\n"+msg[:1992]+"```")


@commands.command(aliases=['beavis.zen'])
async def beavis.zensay(self, *, txt:str):
  msg = await self.do_cowsay(txt, 'beavis.zen')
  await self.bot.say("```\n"+msg[:1992]+"```")


@commands.command(aliases=['kitty'])
async def kittysay(self, *, txt:str):
  msg = await self.do_cowsay(txt, 'kitty')
  await self.bot.say("```\n"+msg[:1992]+"```")


@commands.command(aliases=['elephant-in-snake'])
async def elephantinsnakesay(self, *, txt:str):
  msg = await self.do_cowsay(txt, 'elephant-in-snake')
  await self.bot.say("```\n"+msg[:1992]+"```")


@commands.command(aliases=['tux'])
async def tuxsay(self, *, txt:str):
  msg = await self.do_cowsay(txt, 'tux')
  await self.bot.say("```\n"+msg[:1992]+"```")


@commands.command(aliases=['duck'])
async def ducksay(self, *, txt:str):
  msg = await self.do_cowsay(txt, 'duck')
  await self.bot.say("```\n"+msg[:1992]+"```")


@commands.command(aliases=['elephant'])
async def elephantsay(self, *, txt:str):
  msg = await self.do_cowsay(txt, 'elephant')
  await self.bot.say("```\n"+msg[:1992]+"```")


@commands.command(aliases=['sheep'])
async def sheepsay(self, *, txt:str):
  msg = await self.do_cowsay(txt, 'sheep')
  await self.bot.say("```\n"+msg[:1992]+"```")


@commands.command(aliases=['mech'])
async def mechsay(self, *, txt:str):
  msg = await self.do_cowsay(txt, 'mech-and-cow')
  await self.bot.say("```\n"+msg[:1992]+"```")


@commands.command()
async def eyessay(self, *, txt:str):
  msg = await self.do_cowsay(txt, 'eyes')
  await self.bot.say("```\n"+msg[:1992]+"```")


@commands.command(aliases=['ren'])
async def rensay(self, *, txt:str):
  msg = await self.do_cowsay(txt, 'ren')
  await self.bot.say("```\n"+msg[:1992]+"```")


@commands.command(aliases=['kiss'])
async def kisssay(self, *, txt:str):
  msg = await self.do_cowsay(txt, 'kiss')
  await self.bot.say("```\n"+msg[:1992]+"```")


@commands.command(aliases=['skeleton'])
async def skeletonsay(self, *, txt:str):
  msg = await self.do_cowsay(txt, 'skeleton')
  await self.bot.say("```\n"+msg[:1992]+"```")


@commands.command()
async def budfrogssay(self, *, txt:str):
  msg = await self.do_cowsay(txt, 'bud-frogs')
  await self.bot.say("```\n"+msg[:1992]+"```")


@commands.command(aliases=['gbsay'])
async def ghostbusterssay(self, *, txt:str):
  msg = await self.do_cowsay(txt, 'ghostbusters')
  await self.bot.say("```\n"+msg[:1992]+"```")


@commands.command(aliases=['milk'])
async def milksay(self, *, txt:str):
  msg = await self.do_cowsay(txt, 'milk')
  await self.bot.say("```\n"+msg[:1992]+"```")


@commands.command()
async def lukekoalasay(self, *, txt:str):
  msg = await self.do_cowsay(txt, 'luke-koala')
  await self.bot.say("```\n"+msg[:1992]+"```")


@commands.command(aliases=['moose'])
async def moosesay(self, *, txt:str):
  msg = await self.do_cowsay(txt, 'moose')
  await self.bot.say("```\n"+msg[:1992]+"```")


@commands.command(aliases=['vader'])
async def vadersay(self, *, txt:str):
  msg = await self.do_cowsay(txt, 'vader')
  await self.bot.say("```\n"+msg[:1992]+"```")


@commands.command(aliases=['kosh'])
async def koshsay(self, *, txt:str):
  msg = await self.do_cowsay(txt, 'kosh')
  await self.bot.say("```\n"+msg[:1992]+"```")


@commands.command(aliases=['snowman'])
async def snowmansay(self, *, txt:str):
  msg = await self.do_cowsay(txt, 'snowman')
  await self.bot.say("```\n"+msg[:1992]+"```")


@commands.command(aliases=['suse'])
async def susesay(self, *, txt:str):
  msg = await self.do_cowsay(txt, 'suse')
  await self.bot.say("```\n"+msg[:1992]+"```")


@commands.command(aliases=['hellokitty'])
async def hellokittysay(self, *, txt:str):
  msg = await self.do_cowsay(txt, 'hellokitty')
  await self.bot.say("```\n"+msg[:1992]+"```")


@commands.command(aliases=['mutilated'])
async def mutilatedsay(self, *, txt:str):
  msg = await self.do_cowsay(txt, 'mutilated')
  await self.bot.say("```\n"+msg[:1992]+"```")


@commands.command(aliases=['cock'])
async def cocksay(self, *, txt:str):
  msg = await self.do_cowsay(txt, 'cock')
  await self.bot.say("```\n"+msg[:1992]+"```")


@commands.command(aliases=['headin'])
async def headinsay(self, *, txt:str):
  msg = await self.do_cowsay(txt, 'head-in')
  await self.bot.say("```\n"+msg[:1992]+"```")


@commands.command(aliases=['cheese'])
async def cheesesay(self, *, txt:str):
  msg = await self.do_cowsay(txt, 'cheese')
  await self.bot.say("```\n"+msg[:1992]+"```")


@commands.command(aliases=['calvin'])
async def calvinsay(self, *, txt:str):
  msg = await self.do_cowsay(txt, 'calvin')
  await self.bot.say("```\n"+msg[:1992]+"```")


@commands.command(aliases=['3eyes'])
async def threeeyessay(self, *, txt:str):
  msg = await self.do_cowsay(txt, 'three-eyes')
  await self.bot.say("```\n"+msg[:1992]+"```")


@commands.command(aliases=['bunny'])
async def bunnysay(self, *, txt:str):
  msg = await self.do_cowsay(txt, 'bunny')
  await self.bot.say("```\n"+msg[:1992]+"```")