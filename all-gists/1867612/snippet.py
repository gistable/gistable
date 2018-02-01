class Kalman:
	"""
	USAGE:
	
	# e.g., tracking an (x,y) point over time
	k = Kalman(state_dim = 6, obs_dim = 2)
	
	# when you get a new observation — 
	someNewPoint = np.r_[1,2]
	k.update(someNewPoint)
	
	# and when you want to make a new prediction
	predicted_location = k.predict()
	
	
	NOTE: 
	Setting state_dim to 3*obs_dim automatically implements a simple
	acceleration-based model, i.e.
	x(t+1) = x(t) + v(t) + a(t)/2
	
	You're free to implement whichever model you like by setting state_dim
	to what you need, and then directly modifying the "A" matrix.

	The text that helped me most with understanding Kalman filters is here:
	http://www.njfunk.com/research/courses/652-probability-report.pdf
	"""
	import numpy as np
	def __init__(self, state_dim, obs_dim):
		self.state_dim = state_dim
		self.obs_dim   = obs_dim
		
		self.Q 		 = np.matrix( np.eye(state_dim)*1e-4 )			  # Process noise
		self.R		 = np.matrix( np.eye(obs_dim)*0.01 )			  # Observation noise
		self.A		 = np.matrix( np.eye(state_dim) )			  # Transition matrix
		self.H		 = np.matrix( np.zeros((obs_dim, state_dim)) )		  # Measurement matrix
		self.K		 = np.matrix( np.zeros_like(self.H.T) )			  # Gain matrix
		self.P		 = np.matrix( np.zeros_like(self.A) )			  # State covariance
		self.x		 = np.matrix( np.zeros((state_dim, 1)) )		  # The actual state of the system
	
		if obs_dim == state_dim/3:
			# We'll go ahead and make this a position-predicting matrix with velocity & acceleration if we've got the right combination of dimensions
			# The model is : x( t + 1 ) = x( t ) + v( t ) + a( t ) / 2

			idx = np.r_[0:obs_dim]
			positionIdx = np.ix_(idx, idx)
			velocityIdx = np.ix_(idx,idx+obs_dim)
			accelIdx	= np.ix_(idx, idx+obs_dim*2)
			accelAndVelIdx = np.ix_(idx+obs_dim, idx+obs_dim*2)
			
			self.H[positionIdx]		= np.eye(obs_dim)
			self.A				= np.eye(state_dim)
			self.A[velocityIdx]		+= np.eye(obs_dim)
			self.A[accelIdx]		+= 0.5 * np.eye(obs_dim)
			self.A[accelAndVelIdx]  	+= np.eye(obs_dim)
			
	def update(self, obs):
		
		if obs.ndim == 1:
			obs = np.matrix(obs).T
		
		# Make prediction
		self.x	= self.A * self.x
		self.P	= self.A * self.P * self.A.T + self.Q
		
		# Compute the optimal Kalman gain factor
		self.K = self.P * self.H.T * inv(self.H * self.P * self.H.T + self.R)
		
		# Correction based on observation
		self.x = self.x + self.K * ( obs - self.H * self.x )
		self.P = self.P - self.K * self.H * self.P


	def predict(self):
		return np.asarray(self.H*self.x)
