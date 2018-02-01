render
	for each particle
		x, y = particle.position

		color = sample( colorMap, x, y )
		noise = sample( noiseMap, x, y )

		angle = noise * PI * 2

		particle.velocity.add( cos(angle), sin(angle) )
		particle.velocity.normalize()

		drawParticle( particle, color )

		#a crude way of killing off particles ...
		particle.life -= drain

		if (particle.life < 0)
			particle.life = 1
			particle.resetPosition()