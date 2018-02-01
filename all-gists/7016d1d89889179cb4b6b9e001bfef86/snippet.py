image_mimes = ['image/png', 'image/pjpeg', 'image/jpeg', 'image/x-icon']
async def isimage(url:str):
	try:
		with aiohttp.ClientSession() as session:
			with aiohttp.Timeout(30):
				async with session.get(url) as resp:
					if resp.status == 200:
						mime = resp.headers.get('Content-type', '').lower()
						if any([mime == x for x in image_mimes]):
							return True
						else:
							return False
	except:
		return False

async def isgif(url:str):
	try:
		with aiohttp.ClientSession() as session:
			with aiohttp.Timeout(30):
				async with session.get(url) as resp:
					if resp.status == 200:
						mime = resp.headers.get('Content-type', '').lower()
						if mime == "image/gif":
							return True
						else:
							return False
	except:
		return False

async def get_images(ctx, **kwargs):
	try:
		message = ctx.message
		channel = ctx.message.channel
		attachments = ctx.message.attachments
		mentions = ctx.message.mentions
		limit = kwargs.pop('limit', None)
		urls = kwargs.pop('urls', [])
		gif = kwargs.pop('gif', False)
		if gif:
			check_func = isgif
		else:
			check_func = isimage
		if urls is None:
			urls = []
		elif type(urls) != tuple:
			urls = [urls]
		else:
			urls = list(urls)
		scale = kwargs.pop('scale', None)
		scale_msg = None
		int_scale = None
		if gif is False:
			for mention in mentions:
				urls.append(mention.avatar_url)
		for attachment in attachments:
			urls.append(attachment['url'])
		if scale:
			scale_limit = scale
			if limit:
				limit += 1
		if limit and urls and len(urls) > limit:
			await bot.send_message(channel, ':no_entry: `Max image limit (<= {0})`'.format(limit))
			ctx.command.reset_cooldown(ctx)
			return False
		img_urls = []
		count = 1
		for url in urls:
			if url.startswith('<@'):
				continue
			try:
				if scale:
					if str(math.floor(float(url))).isdigit():
						int_scale = int(math.floor(float(url)))
						scale_msg = '`Scale: {0}`\n'.format(int_scale)
						if int_scale > scale_limit and ctx.message.author.id != bot.owner.id:
							int_scale = scale_limit
							scale_msg = '`Scale: {0} (Limit: <= {1})`\n'.format(int_scale, scale_limit)
						continue
			except:
				pass
			check = await check_func(url)
			if check is False and gif is False:
				check = await isgif(url)
				if check:
					await bot.send_message(channel, ":warning: This command is for images, not gifs (use `gmagik` or `gascii`)!")
					ctx.command.reset_cooldown(ctx)
					return False
				elif len(img_urls) == 0:
					await bot.send_message(channel, 'Invalid or Non-Image(s)!')
					ctx.command.reset_cooldown(ctx)
					return False
				else:
					await bot.send_message(channel, ':warning: Image `{0}` is Invalid!'.format(count))
					continue
			elif gif and check is False:
				check = await isimage(url)
				if check:
					await bot.send_message(channel, ":warning: This command is for gifs, not images (use `magik`)!")
					ctx.command.reset_cooldown(ctx)
					return False
				elif len(img_urls) == 0:
					await bot.send_message(channel, 'Invalid or Non-Gifs(s)!')
					ctx.command.reset_cooldown(ctx)
					return False
				else:
					await bot.send_message(channel, ':warning: Gif `{0}` is Invalid!'.format(count))
					continue
			img_urls.append(url)
			count += 1
		else:
			if len(img_urls) == 0:
				last_attachment = None
				async for message in bot.logs_from(channel, limit=25):
					if message.attachments:
						last_attachment = message.attachments[0]['url']
						check = await check_func(last_attachment)
					elif message.embeds:
						last_attachment = message.embeds[0]['url']
						check = await check_func(last_attachment)
						if check:
							img_urls.append(last_attachment)
							break
						else:
							continue
				if len(img_urls) == 0:
					await bot.send_message(channel, ":no_entry: Please input url(s){0}or atachment(s).".format(', mention(s) ' if not gif else ' '))
					ctx.command.reset_cooldown(ctx)
					return False
		if scale:
			return img_urls, int_scale, scale_msg
		return img_urls
	except Exception as e:
		print(e)