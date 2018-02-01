############################################################################################
##
## Quick IOCTL Decoder!
##
## All credit for actual IOCTL decode logic:
##      http://www.osronline.com/article.cfm?article=229
## 
##
## To install:
##      Copy script into plugins directory, i.e: C:\Program Files\IDA 6.8\plugins
##
## To run:
##      Highlight IOCTL then right click and select "Decode IOCTL" or press PLUGIN_HOTKEY
##      The decoded IOCTL data will be added as a comment and displayed in the IDA cli
##
############################################################################################

__VERSION__ = '0.1'
__AUTHOR__ = '@herrcore'

PLUGIN_NAME = "Quick IOCTL Decoder"
PLUGIN_HOTKEY = 'Ctrl-Alt-I'


import idaapi

class IOCTL_Decoder():
    DEVICE = [None]*55
    DEVICE[1]="BEEP"
    DEVICE[2]="CD_ROM"
    DEVICE[3]="CD_ROM_FILE_SYSTEM"
    DEVICE[4]="CONTROLLER"
    DEVICE[5]="DATALINK"
    DEVICE[6]="DFS"
    DEVICE[7]="DISK"
    DEVICE[8]="DISK_FILE_SYSTEM"
    DEVICE[9]="FILE_SYSTEM"
    DEVICE[10]="INPORT_PORT"
    DEVICE[11]="KEYBOARD"
    DEVICE[12]="MAILSLOT"
    DEVICE[13]="MIDI_IN"
    DEVICE[14]="MIDI_OUT"
    DEVICE[15]="MOUSE"
    DEVICE[16]="MULTI_UNC_PROVIDER"
    DEVICE[17]="NAMED_PIPE"
    DEVICE[18]="NETWORK"
    DEVICE[19]="NETWORK_BROWSER"
    DEVICE[20]="NETWORK_FILE_SYSTEM"
    DEVICE[21]="NULL"
    DEVICE[22]="PARALLEL_PORT"
    DEVICE[23]="PHYSICAL_NETCARD"
    DEVICE[24]="PRINTER"
    DEVICE[25]="SCANNER"
    DEVICE[26]="SERIAL_MOUSE_PORT"
    DEVICE[27]="SERIAL_PORT"
    DEVICE[28]="SCREEN"
    DEVICE[29]="SOUND"
    DEVICE[30]="STREAMS"
    DEVICE[31]="TAPE"
    DEVICE[32]="TAPE_FILE_SYSTEM"
    DEVICE[33]="TRANSPORT"
    DEVICE[34]="UNKNOWN"
    DEVICE[35]="VIDEO"
    DEVICE[36]="VIRTUAL_DISK"
    DEVICE[37]="WAVE_IN"
    DEVICE[38]="WAVE_OUT"
    DEVICE[39]="8042_PORT"
    DEVICE[40]="NETWORK_REDIRECTOR"
    DEVICE[41]="BATTERY"
    DEVICE[42]="BUS_EXTENDER"
    DEVICE[43]="MODEM"
    DEVICE[44]="VDM"
    DEVICE[45]="MASS_STORAGE"
    DEVICE[46]="SMB"
    DEVICE[47]="KS"
    DEVICE[48]="CHANGER"
    DEVICE[49]="SMARTCARD"
    DEVICE[50]="ACPI"
    DEVICE[51]="DVD"
    DEVICE[52]="FULLSCREEN_VIDEO"
    DEVICE[53]="DFS_FILE_SYSTEM"
    DEVICE[54]="DFS_VOLUME"

    def __init__(self, control_code):
        self.control_code = control_code

    def decode(self):
        out={}
        device_val = (self.control_code >> 16) & 0xFFF
        funcVal = (self.control_code >> 2) & 0xFFF
        if (device_val <= 54) and (device_val != 0):
            device_string = self.DEVICE[device_val]+ " ("+hex(device_val)+")"
        else:
            device_string = hex(device_val)
        function_string = hex(funcVal)
        out["device"] = device_string
        out["function"] = function_string
        access = (self.control_code >> 14) & 3   
        method = self.control_code & 3
        access_string = ""
        if access == 0:
            access_string = "FILE_ANY_ACCESS"
        elif access == 1:
            access_string = "FILE_READ_ACCESS"
        elif access == 2:
            access_string = "FILE_WRITE_ACCESS"
        elif access == 3:
            access_string = "Read and Write"
        method_string = ""
        if method == 0:
            method_string = "METHOD_BUFFERED"
        elif method == 1:
            method_string = "METHOD_IN_DIRECT"
        elif method == 2:
            method_string = "METHOD_OUT_DIRECT"
        elif method == 3:
            method_string = "METHOD_NEITHER"
        out["access"] = access_string
        out["method"] = method_string
        return out


class IDAIOCTLDecoder():
    @staticmethod
    def decode():
        ea = ScreenEA()
        if ea == idaapi.BADADDR:
            idaapi.msg(PLUGIN_NAME + " ERROR: Could not get get_screen_ea()")
            return

        str_id = idaapi.get_highlighted_identifier()
        if not str_id:
            idaapi.msg(PLUGIN_NAME + " ERROR: No Ioctl Code highlighted!")
            return
        try:
            if str_id[-1] == 'h':
                code = int(str_id[:-1], 16)
            elif str_id[-1] == 'o':
                code = int(str_id[:-1], 8)
            elif str_id[-1] == 'b':
                code = int(str_id[:-1], 2)
            else:
                code = int(str_id)
        except ValueError:
            idaapi.msg(PLUGIN_NAME + " ERROR: Not a valid Ioctl Code: " + str(str_id)) 
            return

        try:
            decoder = IOCTL_Decoder(code)
            ioctl_data = decoder.decode()

            #print decoded IOCTL to cli
            msg_string =  "That IOCTL decodes to: \n\tDevice: %s \n\tFunction: %s \n\tAccess: %s \n\tMethod: %s" 
            idaapi.msg(msg_string % (ioctl_data["device"], ioctl_data["function"], ioctl_data["access"], ioctl_data["method"]))

            #add decoded IOCTL as comment
            comment_string =  "dwIoControlCode: \n\t\tDevice: %s \n\t\tFunction: %s \n\t\tAccess: %s \n\t\tMethod: %s"
            idaapi.set_cmt(ea, comment_string % (ioctl_data["device"], ioctl_data["function"], ioctl_data["access"], ioctl_data["method"]), 0)
        except Exception as e:
             idaapi.msg(PLUGIN_NAME + " ERROR: " + str(e))
        return


class IOCTLDecodeHandler(idaapi.action_handler_t):
    def activate(self, ctx):
        IDAIOCTLDecoder.decode()

    def update(self, ctx):
        return idaapi.AST_ENABLE_ALWAYS

class QuickIOCTLDecoderHooks(idaapi.UI_Hooks):
    def finish_populating_tform_popup(self, form, popup):
        tft = idaapi.get_tform_type(form)
        if tft == idaapi.BWN_DISASM:
            # Note the 'None' as action name (1st parameter).
            # That's because the action will be deleted immediately
            # after the context menu is hidden anyway, so there's
            # really no need giving it a valid ID.
            desc = idaapi.action_desc_t(None, 'Decode IOCTL', IOCTLDecodeHandler())
            idaapi.attach_dynamic_action_to_popup(form, popup, desc, None)

class QuickIOCTLDecoder(idaapi.plugin_t):
    flags = idaapi.PLUGIN_UNL
    comment = "Decode IOCTL codes!"

    help = "Highlight IOCTL and right-click 'Decode IOCTL'"
    wanted_name = PLUGIN_NAME
    wanted_hotkey = PLUGIN_HOTKEY
    
 
    def init(self):
        idaapi.msg("Initializing: %s\n" % PLUGIN_NAME)
        global hooks
        hooks = QuickIOCTLDecoderHooks()
        re = hooks.hook()
        return idaapi.PLUGIN_OK

        
    def run(self, arg):
        IDAIOCTLDecoder.decode()
        pass

    def term(self):
        pass

def PLUGIN_ENTRY():
    return QuickIOCTLDecoder()




