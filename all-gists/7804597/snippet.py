#python

'''

	Notifier Command

	Demonstrates how to write an executable and queryable command.
	The difference is that this command will listen for state changes
	in a scene. If the selection changes, then the command will check
	its enable/disable state and force any form it's embedded into
	to update.
	
'''

import lx
import lxifc
import lxu.select
import lxu.command

SERVER_NAME = "item.size"
ARG_SIZE = "size"

class Command (lxu.command.BasicCommand):
	
	def __init__ (self):
		
		'''
			In the constructor, we set the arguments for the command.
			The basic_Flags method allows the properties of the
			argument to be set, for example, setting the argument
			to queryable will make it queryable...duh. The flags are
			set by index in the order the commands are added.
		'''
		
		lxu.command.BasicCommand.__init__(self)
		
		self.dyna_Add (ARG_SIZE, lx.symbol.sTYPE_FLOAT)
		self.basic_SetFlags (0, lx.symbol.fCMDARG_QUERY)
		
		self.sel_svc = lx.service.Selection ()
		self.not_svc = lx.service.NotifySys ()
		self.scene = lxu.select.SceneSelection ().current ()
		
		self.notifier = lx.object.Notifier ()
		
		self.locator_type = self.scn_svc.ItemTypeLookup (lx.symbol.sITYPE_LOCATOR)
		
	def cmd_Flags (self):
		
		'''
			This function sets the flags. These basically mean
			that the command performs scene/model changes. In
			other words, it makes changes that the user would
			expect to be undoable. This command changes channel
			values, so it definitely needs to be undoable.
		'''
		
        	return lx.symbol.fCMD_MODEL | lx.symbol.fCMD_UNDO
        	
        def basic_Enable (self, msg):
        	
        	'''
        		The enable function is used to set the enable/disable
        		state of the command. Returning true makes the command
        		enabled and returning false makes the command disabled.
        	'''
        	
        	if len (lxu.select.ItemSelection ().current ()) > 0:
        		return True
        	else:
        		return False
        		
        def basic_Execute (self, msg, flags):
        	
        	'''
        		As the name suggests, the execute method is called
        		when the command is executed. We can at this point get
        		the value of any arguments and do what we need to do.
        		Success or failure is handled through an ILxMessage
        		object which can be initialized using the second
        		argument to the function.
        	'''
        	
        	message = lx.object.Message (msg)
        	
        	item_sel = lxu.select.ItemSelection ().current ()
        	chan_write = lx.object.ChannelWrite (self.scene.Channels (lx.symbol.s_ACTIONLAYER_EDIT, self.sel_svc.GetTime ())
        	
        	'''
        		Read the size argument. This is done by index, in the
        		order they were added to the command in the constructor.
        	'''
        	
        	if self.dyna_IsSet (0) != True:
			message.SetCode (lx.result.CMD_MISSING_ARGS)
        		return
		
		arg_value = self.attr_GetFlt(0)

		'''
			Loop through the items and set their size channel.
		'''

        	for item in item_sel:
        		if item.TestType (self.locator_type) == True:
        			channel = item.ChannelLookup (lx.symbol.sICHAN_LOCATOR_SIZE)
        			chan_write.Double (item, channel, size_arg)

	def cmd_Query (self, index, vaQuery):
		
		'''
			The query functions is called when a particular
			argument is queried. The index function argument
			is the index of the command argument that is being
			queried. the vaQuery is an ILxValueArray object
			that we use to return an array of values. If the
			values are mixed (for example a multiple selection),
			modo will return "(mixed)", otherwise it will return
			the value that we return in the value array.
		'''
		
		val_array = lx.object.ValueArray (vaQuery)
		
		item_sel = lxu.select.ItemSelection ().current ()
        	chan_read = self.scene.Channels (lx.symbol.s_ACTIONLAYER_EDIT, self.sel_svc.GetTime ()

		'''
			If the index doesn't match one of our queryable
			arguments, return early, because who knows what
			they're trying to query.
		'''
		
		if index != 0:
			return

		'''
			Loop through the items and get their size channel,
			add the value to the value array.
		'''

        	for item in item_sel:
        		if item.TestType (self.locator_type) == True:
        			channel = item.ChannelLookup (lx.symbol.sICHAN_LOCATOR_SIZE)
        			value = chan_read.Double (item, channel)
        			val_array.AddFloat (value)
        			
	def cmd_NotifyAddClient (self, argument, object):
        
        	'''
        		Add a single notifier to the command. This will
        		send disable events when the item selection changes.
        	'''
        
		self.notifier = self.not_svc.Spawn ("select.event", "item +d")
        	self.notifier.AddClient (object)
        
    	def cmd_NotifyRemoveClient (self, object):
        
        	'''
            		Remove the notifier.
        	'''
        
        	self.notifier.RemoveClient (object)

'''
	Bless the class, initializing the server.
'''
lx.bless (Command, SERVER_NAME)