import hexchat
 
__module_name__        = "novoice"
__module_version__     = "2.0"
__module_description__ = "Ignores voice messages from ChanServ"
 
def voice_event(word, word_eol, userdata):
    return hexchat.EAT_HEXCHAT
 
hexchat.hook_print("Channel Voice", voice_event)
hexchat.hook_print("Channel DeVoice", voice_event)