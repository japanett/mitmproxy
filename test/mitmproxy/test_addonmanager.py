import pytest

from mitmproxy import addonmanager
from mitmproxy import exceptions
from mitmproxy import options
from mitmproxy import master
from mitmproxy import proxy
from mitmproxy.test import taddons
from mitmproxy.test import tflow


class TAddon:
    def __init__(self, name, addons=None):
        self.name = name
        self.tick = True
        self.custom_called = False
        if addons:
            self.addons = addons

    def __repr__(self):
        return "Addon(%s)" % self.name

    def done(self):
        pass

    def event_custom(self):
        self.custom_called = True


class THalt:
    def event_custom(self):
        raise exceptions.AddonHalt


class AOption:
    def load(self, l):
        l.add_option("custom_option", bool, False, "help")


def test_halt():
    o = options.Options()
    m = master.Master(o, proxy.DummyServer(o))
    a = addonmanager.AddonManager(m)
    halt = THalt()
    end = TAddon("end")
    a.add(halt)
    a.add(end)

    a.trigger("custom")
    assert not end.custom_called

    a.remove(halt)
    a.trigger("custom")
    assert end.custom_called


def test_lifecycle():
    o = options.Options()
    m = master.Master(o, proxy.DummyServer(o))
    a = addonmanager.AddonManager(m)
    a.add(TAddon("one"))

    with pytest.raises(exceptions.AddonError):
        a.add(TAddon("one"))
    with pytest.raises(exceptions.AddonError):
        a.remove(TAddon("nonexistent"))

    f = tflow.tflow()
    a.handle_lifecycle("request", f)

    a._configure_all(o, o.keys())


def test_simple():
    with taddons.context() as tctx:
        a = tctx.master.addons

        assert len(a) == 0
        a.add(TAddon("one"))
        assert a.get("one")
        assert not a.get("two")
        assert len(a) == 1
        a.clear()
        assert len(a) == 0
        assert not a.chain

        a.add(TAddon("one"))
        a.trigger("done")
        a.trigger("tick")
        tctx.master.has_log("not callable")

        a.remove(a.get("one"))
        assert not a.get("one")

        ta = TAddon("one")
        a.add(ta)
        a.trigger("custom")
        assert ta.custom_called


def test_load_option():
    o = options.Options()
    m = master.Master(o, proxy.DummyServer(o))
    a = addonmanager.AddonManager(m)
    a.add(AOption())
    assert "custom_option" in m.options._options


def test_nesting():

    o = options.Options()
    m = master.Master(o, proxy.DummyServer(o))
    a = addonmanager.AddonManager(m)

    a.add(
        TAddon(
            "one",
            addons=[
                TAddon("two"),
                TAddon("three", addons=[TAddon("four")])
            ]
        )
    )
    assert len(a.chain) == 1
    assert a.get("one")
    assert a.get("two")
    assert a.get("three")
    assert a.get("four")

    a.trigger("custom")
    assert a.get("one").custom_called
    assert a.get("two").custom_called
    assert a.get("three").custom_called
    assert a.get("four").custom_called

    a.remove(a.get("three"))
    assert not a.get("three")
    assert not a.get("four")
