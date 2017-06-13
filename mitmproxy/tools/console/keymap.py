import typing
from mitmproxy.tools.console import commandeditor
from mitmproxy.tools.console import signals
import ruamel.yaml


Contexts = {
    "chooser",
    "commands",
    "eventlog",
    "flowlist",
    "flowview",
    "global",
    "grideditor",
    "help",
    "keybindings",
    "options",
}


class Binding:
    def __init__(self, key, command, contexts, help):
        self.key, self.command, self.contexts = key, command, sorted(contexts)
        self.help = help

    def keyspec(self):
        """
            Translate the key spec from a convenient user specification to one
            Urwid understands.
        """
        return self.key.replace("space", " ")

    def sortkey(self):
        return self.key + ",".join(self.contexts)

    @classmethod
    def from_dict(klass, d):
        return klass(**d)

    def to_dict(self, strip=False):
        cmd = self.command
        if strip:
            cmd = cmd.strip()
        return dict(
            key=self.key,
            command=cmd,
            contexts=self.contexts,
            help=self.help
        )

    def __eq__(self, other):
        return self.to_dict(True) == other.to_dict(True)


class Keymap:
    def __init__(self, master):
        self.executor = commandeditor.CommandExecutor(master)
        self.keys = {}
        self.bindings = []
        self._update()

    def _update(self):
        self.keys = {i: {} for i in Contexts}
        for idx, b in enumerate(self.bindings[:]):
            if b.contexts:
                for c in b.contexts:
                    self.keys[c][b.keyspec()] = b
            else:
                del self.bindings[idx]
        signals.keybindings_change.send(self)

    def _check_contexts(self, contexts):
        if not contexts:
            raise ValueError("Must specify at least one context.")
        for c in contexts:
            if c not in Contexts:
                raise ValueError("Unsupported context: %s" % c)

    def bulk(self, bindings):
        for b in bindings:
            self.add(**b.to_dict())

    def add(
        self,
        key: str,
        command: str,
        contexts: typing.Sequence[str],
        help=""
    ) -> None:
        """
            Add a key to the key map.
        """
        self._check_contexts(contexts)
        for b in self.bindings:
            if b.key == key and b.command.strip() == command.strip():
                b.contexts = sorted(list(set(b.contexts + contexts)))
                if help:
                    b.help = help
                break
        else:
            b = Binding(key=key, command=command, contexts=contexts, help=help)
            self.bindings.append(b)
        self._update()

    def remove(self, key: str, contexts: typing.Sequence[str]) -> None:
        """
            Remove a key from the key map.
        """
        self._check_contexts(contexts)
        for c in contexts:
            b = self.get(c, key)
            if b:
                # Modify the binding in place. If this gives an empty context,
                # it will be removed in _update.
                b.contexts = [x for x in b.contexts if x != c]
        self._update()

    def get(self, context: str, key: str) -> typing.Optional[Binding]:
        if context in self.keys:
            return self.keys[context].get(key, None)
        return None

    def list(self, context: str) -> typing.Sequence[Binding]:
        b = [x for x in self.bindings if context in x.contexts or context == "all"]
        single = [x for x in b if len(x.key.split()) == 1]
        multi = [x for x in b if len(x.key.split()) != 1]
        single.sort(key=lambda x: x.sortkey())
        multi.sort(key=lambda x: x.sortkey())
        return single + multi

    def handle(self, context: str, key: str) -> typing.Optional[str]:
        """
            Returns the key if it has not been handled, or None.
        """
        b = self.get(context, key) or self.get("global", key)
        if b:
            return self.executor(b.command)
        return key

    def dump(self) -> str:
        bindings = []
        for b in self.list("all"):
            bindings.append(b.to_dict())
        unbindings = []
        data = {}
        if bindings:
            data["bind"] = bindings
        if unbindings:
            data["unbind"] = unbindings
        return ruamel.yaml.dump(data)

    def load(self, inp: str) -> None:
        d = ruamel.yaml.safe_load(inp)
        print(d)
        for bd in d.get("bind", []):
            print(Binding.from_dict(bd))
        for bd in d.get("unbind", []):
            print(bd)
