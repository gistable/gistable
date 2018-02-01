#############################################################################
# Weechat cowsay plugin, sends messages with a low priority in the current
# buffer, used /cowchat <cowfile> <message>
#
# Written by telnoratti <telnoratti@telnor.org>
#
# Copyright (c) 2013, Telnor Institute
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.


import weechat

weechat.register("cowchat", "cowchat", "0.4", "BSD", "Cowchat!", "", "utf-8")

def cowcall(data, buffer, args):
    cowfile, sep, say = args.partition(" ")
    if cowfile == "" or say == "":
        return weechat.WEECHAT_RC_ERROR
    server, sep, channel = weechat.buffer_get_string(buffer, "name").partition("#")
    server = server[0:-1]
    channel = ''.join([sep, channel])
    weechat.hook_process("cowsay -f {0} {1}".format(cowfile, say),
                         2000,
                         "cowchat",
                         "{0};{1}".format(server, channel))
    return weechat.WEECHAT_RC_OK

def cowchat(data, command, return_code, out, err):
    for line in out.split("\n"):
        if len(line) > 0 and line[0] == '/':
            line = '/' + line
        weechat.hook_signal_send("irc_input_send", weechat.WEECHAT_HOOK_SIGNAL_STRING,
                                 "{0};2;;{1}".format(data, line))
    return weechat.WEECHAT_RC_OK


hook = weechat.hook_command("cowchat", "Pastes a cowsay into the current buffer",
                            "word | text",
                            "<cow> <say>",
                            "",
                            "cowcall", "")