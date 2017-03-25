import os
import importlib
import threading
import sys

from mitmproxy import addonmanager
from mitmproxy import exceptions
from mitmproxy import ctx

import watchdog.events
from watchdog.observers import polling


def load_script(path):
    loader = importlib.machinery.SourceFileLoader(os.path.basename(path), path)
    try:
        oldpath = sys.path
        sys.path.insert(0, os.path.dirname(path))
        with addonmanager.safecall(propagate=False):
            m = loader.load_module()
            if not getattr(m, "name", None):
                m.name = path
            return m
    finally:
        sys.path[:] = oldpath


class ReloadHandler(watchdog.events.FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback

    def filter(self, event):
        """
            Returns True only when .py file is changed
        """
        if event.is_directory:
            return False
        if os.path.basename(event.src_path).startswith("."):
            return False
        if event.src_path.endswith(".py"):
            return True
        return False

    def on_modified(self, event):
        if self.filter(event):
            self.callback()

    def on_created(self, event):
        if self.filter(event):
            self.callback()


class Script:
    """
        An addon that manages a single script.
    """
    def __init__(self, path):
        self.name = "scriptmanager:" + path
        self.path = path
        self.ns = None
        self.observer = None
        self.dead = False

        self.last_options = None
        self.should_reload = threading.Event()

    def load(self, l):
        try:
            self.ns = load_script(self.path)
        except FileNotFoundError:
            ctx.log("%s: file not found." % self.path)

    @property
    def addons(self):
        if self.ns is not None and not self.dead:
            return [self.ns]
        return []

    def reload(self):
        self.should_reload.set()

    def tick(self):
        if self.should_reload.is_set():
            self.should_reload.clear()
            ctx.log.info("Reloading script: %s" % self.name)
            if self.ns:
                self.addons.remove(self.ns)
            self.ns = load_script(self.path)
            ctx.master.addons.register(self.ns)
            self.configure(self.last_options, self.last_options.keys())

    def configure(self, options, updated):
        self.last_options = options
        if not self.observer:
            self.observer = polling.PollingObserver()
            # Bind the handler to the real underlying master object
            self.observer.schedule(
                ReloadHandler(self.reload),
                os.path.dirname(self.path) or "."
            )
            self.observer.start()

    def done(self):
        self.dead = True


class ScriptLoader:
    """
        An addon that manages loading scripts from options.
    """
    def __init__(self):
        self.is_running = False
        self.addons = []

    def running(self):
        self.is_running = True

    def run_once(self, command, flows):
        # Returning once we have proper commands
        raise NotImplementedError

    def configure(self, options, updated):
        if "scripts" in updated:
            for s in options.scripts:
                if options.scripts.count(s) > 1:
                    raise exceptions.OptionsError("Duplicate script: %s" % s)

            for a in self.addons:
                if a.name not in options.scripts:
                    ctx.log.info("Un-loading script: %s" % a.name)
                    ctx.master.addons.remove(a)
                    self.addons.remove(a)

            # The machinations below are to ensure that:
            #   - Scripts remain in the same order
            #   - Scripts are not initialized un-necessarily. If only a
            #   script's order in the script list has changed, it is just
            #   moved.

            current = {}
            for a in self.addons:
                current[a.name] = a

            ordered = []
            newscripts = []
            for s in options.scripts:
                if s in current:
                    ordered.append(current[s])
                else:
                    ctx.log.info("Loading script: %s" % s)
                    try:
                        sc = Script(s)
                    except ValueError as e:
                        raise exceptions.OptionsError(str(e))
                    ordered.append(sc)
                    newscripts.append(sc)

            self.addons = ordered

            for s in newscripts:
                ctx.master.addons.register(s)
                if self.is_running:
                    # If we're already running, we configure and tell the addon
                    # we're up and running.
                    ctx.master.addons.invoke_addon(
                        s, "configure", options, options.keys()
                    )
                    ctx.master.addons.invoke_addon(s, "running")
