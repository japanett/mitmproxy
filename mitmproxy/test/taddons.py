import sys
import contextlib

import mitmproxy.master
import mitmproxy.options
from mitmproxy import proxy
from mitmproxy import addonmanager
from mitmproxy import eventsequence


class TestAddons(addonmanager.AddonManager):
    def __init__(self, master):
        super().__init__(master)

    def trigger(self, event, *args, **kwargs):
        if event == "log":
            self.master.logs.append(args[0])
        else:
            self.master.events.append((event, args, kwargs))
        super().trigger(event, *args, **kwargs)


class RecordingMaster(mitmproxy.master.Master):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.addons = TestAddons(self)
        self.events = []
        self.logs = []

    def dump_log(self, outf=sys.stdout):
        for i in self.logs:
            print("%s: %s" % (i.level, i.msg), file=outf)

    def has_log(self, txt, level=None):
        for i in self.logs:
            if level and i.level != level:
                continue
            if txt.lower() in i.msg.lower():
                return True
        return False

    def has_event(self, name):
        for i in self.events:
            if i[0] == name:
                return True
        return False

    def clear(self):
        self.logs = []


class context:
    """
        A context for testing addons, which sets up the mitmproxy.ctx module so
        handlers can run as they would within mitmproxy. The context also
        provides a number of helper methods for common testing scenarios.
    """
    def __init__(self, master = None, options = None):
        self.options = options or mitmproxy.options.Options()
        self.master = master or RecordingMaster(
            options, proxy.DummyServer(options)
        )
        self.wrapped = None

    def __enter__(self):
        self.wrapped = self.master.handlecontext()
        self.wrapped.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.wrapped.__exit__(exc_type, exc_value, traceback)
        self.wrapped = None
        return False

    @contextlib.contextmanager
    def cycle(self, addon, f):
        """
            Cycles the flow through the events for the flow. Stops if a reply
            is taken (as in flow interception).
        """
        f.reply._state = "start"
        for evt, arg in eventsequence.iterate(f):
            h = getattr(addon, evt, None)
            if h:
                h(arg)
                if f.reply.state == "taken":
                    return

    def configure(self, addon, **kwargs):
        """
            A helper for testing configure methods. Modifies the registered
            Options object with the given keyword arguments, then calls the
            configure method on the addon with the updated value.
        """
        with self.options.rollback(kwargs.keys(), reraise=True):
            self.options.update(**kwargs)
            addon.configure(self.options, kwargs.keys())
