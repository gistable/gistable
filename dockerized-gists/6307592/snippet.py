import json
import re

_CONFIGFORMAT = r"""
[
        {
                "newline": {
                        "\\n": "newline",
                        "^$": "end",
                        "\\w": "key"
                },
                "key": {
                        "\\w": "key",
                        " ": "space",
                        ":": "sep"
                },
                "space": {
                        " ": "space",
                        ":": "sep"
                },
                "sep": {
                        "[^\\n]": "value"
                },
                "value": {
                        "[^\\n]": "value",
                        "\\n": "newline"
                },
                "end": {
                }
        },
        "newline"

]
"""


def _make_handler(state, transitions):
    def handler(self, char):
        for regex, state_to in transitions.items():
            if re.match(regex, char):
                self.input = getattr(self, "_" + state_to)
                break
        else:
            raise IllegalTransitionError(state, char)
    return handler

def make_state_machine(filename):
    with open(filename) as json_file:
        transition_table, start_state = json.load(json_file)

    namespace = {"_" + state: _make_handler(state, transitions)
                 for state, transitions in transition_table.items()}
    namespace["input"] = namespace.get("_" + start_state)

    return type("StateMachine", (object, ), namespace)

class IllegalTransitionError(Exception):
    def __init__(self, state, char):
        self._state = state
        self._char = char
    def __str__(self):
        return "There's no transition for state '{}' with input '{}'". format(self._state, self._char)

_well_formed_example = """
username: c.schramm
real_name: Christian Schramm
hobbies : meta-programming, drinking beer, playing piano
"""

_malformed_example = """
username: c.schramm
real name: Christian Schramm
hobbies : meta-programming, drinking beer, playing piano
"""

if __name__ == "__main__":
    # I do that dance because I don't want to change the
    # API of make_state_machine, but still want this
    # to be a stand-alone file
    from tempfile import NamedTemporaryFile
    with NamedTemporaryFile(mode="w+") as json_file:
        json_file.write(_CONFIGFORMAT)
        json_file.flush()
        json_file.seek(0)
        StateMachine = make_state_machine(json_file.name)

    # works
    state_machine = StateMachine()
    for char in _well_formed_example:
        state_machine.input(char)

    # fails
    state_machine = StateMachine()
    for char in _malformed_example:
        state_machine.input(char)
