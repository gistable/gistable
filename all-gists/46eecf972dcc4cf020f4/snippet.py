#!/usr/bin/env python
""" pybcompgen

    Pybcompgen calculates context sensitive tab-completion data which is
    derived from environment bash system settings.  It doesn't need to know
    anything about whether you use /etc/completion or /etc/bash_completion.d,
    all that matters is whether *bash* knows about the completion.  The benefit
    of doing this are obvious: you get access to all the completion features
    that the system has installed without caring how the completion features
    work.  Note that this approach doesn't just work for things in the users
    $PATH, it works for arbitrary complex completion. In the default linux
    installations, completion normally includes everything from
    git-subcommands to debian packages, depending on context.

    Example I/O:

       $ pybcompgen "/et"
       ["apt-get "]

       $ pybcompgen "git lo"
       ["log"]

       $ pybcompgen "apt-ge"
       ["apt-get "]

       $ pybcompgen "apt-get inst"
       ["install "]

       $pybcompgen "apt-get install ubuntu-art"
       ["ubuntu-artwork "]
"""
import sys
import unicodedata
from subprocess import Popen, PIPE

def remove_control_characters(s):
    return "".join(ch for ch in s if unicodedata.category(ch)[0]!="C")

def complete(to_complete):
    """ wow! so this is stupid, but what can you do? to understand
        the command required to get completion information out of bash,
        start by executing "printf '/et\x09\x09' | bash -i".  What this
        command does is put bash into interactive mode, then simulate
        typing "/et<tab><tab>" inside bash.  The tab-completion information
        can scraped out of the text, but several things complicate the final
        solution:

        1) the tab-completion info, apart from being post-processed, must be
           scraped from stderr, not from stdout.

        2) for post-processing, without knowledge of how the prompt will be
           rendered or if there is some kind of banner that will be printed,
           it's hard to know where exactly to start capturing tab-completion
           options.

        3) the method used to get the tab completion involves the bash builtins
           "printf", meaning we have to launch subprocess with "bash -c"

        4) completion output could be paginated by bash if there are lots of
           options.  have to account for that and still try to get all the
           options instead of just the first page

        5) sending EOF does not working unless it comes after a newline.  this
           means we have to take extra steps to avoid actually executing the
           command we want to complete (executing the command is not what the
           user expects and is possibly unsafe).  to avoid executing the line,
           after getting tab completion you have to simulate control-a (go to
           start of line) followed by '#'.  this comments the line and prevents
           it from executing.  note: you cannot send control-c to cancel the
           execution of the line because we are dealing with pipes, whereas
           control-c is processed only by proper tty's.
    """
    if not to_complete:
        return []
    cmd = '''bash -c "printf 'echo MARKER\n{complete}\t\t\x01#\necho MARKER'|bash -i"'''.format(complete=to_complete)
    p1 = Popen(cmd, shell=True, stdout=PIPE, stdin=PIPE, stderr=PIPE)
    out, err = p1.communicate()
    lines = err.split('\n')

    first_marker = None
    last_marker = None
    for i in range(len(lines)):
        line = lines[i]
        if line.strip().endswith('echo MARKER'):
            if first_marker is None:
                first_marker = i
            else:
                last_marker = i

    # SPECIAL CASE: pagination
    if last_marker is None:
        # when this happens there are too many options,
        # ie bash is asking something like this:
        #   Display all 103 possibilities? (y or n)
        # Pagination indicators like '--More--'must be removed
        lines = [line for line in lines if not line.startswith('--More')]
        last_marker = len(lines) - 3
        first_marker+=1

    complete_lines = lines[first_marker+2:last_marker-1]

    #SPECIAL-CASE: no completion options or only one option
    if not complete_lines:
        # NOTE:
        #   if there is only one option, readline simply applies it,
        #   which affects the current line in place.  apparently this
        #   results in tons of control-characters being dumped onto
        #   the line, and we have to clean those up for the output
        the_line = lines[first_marker+1:last_marker][0]
        the_line = remove_control_characters(unicode(the_line))
        tmp = the_line[the_line.find(to_complete)+len(to_complete):-4]
        result = to_complete.split()[-1]+tmp
        if '#' in result:
            # this seems to only happen for directories.  not sure why
            result = result[:result.find('#')]
        if result == to_complete.split()[-1]:
            #SPECIAL-CASE: no completion options at all.
            return []
        return [result]
    else:
        # there are multiple completion options
        completion_choices_by_row = [x.split() for x in complete_lines]
        completion_choices = reduce(lambda x,y:x+y, completion_choices_by_row)
        return completion_choices

if __name__=='__main__':
    # if being called from the command line, output json
    # so it is easier for another application to consume
    import json
    result = complete(sys.argv[-1])
    print json.dumps(result)
