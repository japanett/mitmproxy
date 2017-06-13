from mitmproxy.tools.console import keymap


bindings = [
    keymap.Binding(":", "console.command ", ["global"], "Command prompt"),
    keymap.Binding("?", "console.view.help", ["global"], "View help"),
    keymap.Binding("C", "console.view.commands", ["global"], "View commands"),
    keymap.Binding("K", "console.view.keybindings", ["global"], "View key bindings"),
    keymap.Binding("O", "console.view.options", ["global"], "View options"),
    keymap.Binding("E", "console.view.eventlog", ["global"], "View event log"),
    keymap.Binding("Q", "console.exit", ["global"], "Exit immediately"),
    keymap.Binding("q", "console.view.pop", ["global"], "Exit the current view"),
    keymap.Binding("-", "console.layout.cycle", ["global"], "Cycle to next layout"),
    keymap.Binding("shift tab", "console.panes.next", ["global"], "Focus next layout pane"),
    keymap.Binding("P", "console.view.flow @focus", ["global"], "View flow details"),

    keymap.Binding("g", "console.nav.start", ["global"], "Go to start"),
    keymap.Binding("G", "console.nav.end", ["global"], "Go to end"),
    keymap.Binding("k", "console.nav.up", ["global"], "Up"),
    keymap.Binding("j", "console.nav.down", ["global"], "Down"),
    keymap.Binding("l", "console.nav.right", ["global"], "Right"),
    keymap.Binding("h", "console.nav.left", ["global"], "Left"),
    keymap.Binding("tab", "console.nav.next", ["global"], "Next"),
    keymap.Binding("enter", "console.nav.select", ["global"], "Select"),
    keymap.Binding("space", "console.nav.pagedown", ["global"], "Page down"),
    keymap.Binding("ctrl f", "console.nav.pagedown", ["global"], "Page down"),
    keymap.Binding("ctrl b", "console.nav.pageup", ["global"], "Page up"),

    keymap.Binding("i", "console.command set intercept=", ["global"], "Set intercept"),
    keymap.Binding("W", "console.command set save_stream_file=", ["global"], "Stream to file"),
    keymap.Binding("A", "flow.resume @all", ["flowlist", "flowview"], "Resume all intercepted flows"),
    keymap.Binding("a", "flow.resume @focus", ["flowlist", "flowview"], "Resume this intercepted flow"),
    keymap.Binding(
        "b", "console.command cut.save s.content|@focus ''",
        ["flowlist", "flowview"],
        "Save response body to file"
    ),
    keymap.Binding("d", "view.remove @focus", ["flowlist", "flowview"], "Delete flow from view"),
    keymap.Binding("D", "view.duplicate @focus", ["flowlist", "flowview"], "Duplicate flow"),
    keymap.Binding(
        "e",
        """
        console.choose.cmd Format export.formats
        console.command export.file {choice} @focus ''
        """,
        ["flowlist", "flowview"],
        "Export this flow to file"
    ),
    keymap.Binding("f", "console.command set view_filter=", ["flowlist"], "Set view filter"),
    keymap.Binding("F", "set console_focus_follow=toggle", ["flowlist"], "Set focus follow"),
    keymap.Binding(
        "ctrl l",
        "console.command cut.clip ",
        ["flowlist", "flowview"],
        "Send cuts to clipboard"
    ),
    keymap.Binding("L", "console.command view.load ", ["flowlist"], "Load flows from file"),
    keymap.Binding("m", "flow.mark.toggle @focus", ["flowlist"], "Toggle mark on this flow"),
    keymap.Binding("M", "view.marked.toggle", ["flowlist"], "Toggle viewing marked flows"),
    keymap.Binding(
        "n",
        "console.command view.create get https://google.com",
        ["flowlist"],
        "Create a new flow"
    ),
    keymap.Binding(
        "o",
        """
        console.choose.cmd Order view.order.options
        set console_order={choice}
        """,
        ["flowlist"],
        "Set flow list order"
    ),
    keymap.Binding("r", "replay.client @focus", ["flowlist", "flowview"], "Replay this flow"),
    keymap.Binding("S", "console.command replay.server ", ["flowlist"], "Start server replay"),
    keymap.Binding("v", "set console_order_reversed=toggle", ["flowlist"], "Reverse flow list order"),
    keymap.Binding("U", "flow.mark @all false", ["flowlist"], "Un-set all marks"),
    keymap.Binding("w", "console.command save.file @shown ", ["flowlist"], "Save listed flows to file"),
    keymap.Binding("V", "flow.revert @focus", ["flowlist", "flowview"], "Revert changes to this flow"),
    keymap.Binding("X", "flow.kill @focus", ["flowlist"], "Kill this flow"),
    keymap.Binding("z", "view.remove @all", ["flowlist"], "Clear flow list"),
    keymap.Binding("Z", "view.remove @hidden", ["flowlist"], "Purge all flows not showing"),
    keymap.Binding(
        "|",
        "console.command script.run @focus ",
        ["flowlist", "flowview"],
        "Run a script on this flow"
    ),

    keymap.Binding(
        "e",
        """
        console.choose.cmd Part console.edit.focus.options
        console.edit.focus {choice}
        """,
        ["flowview"],
        "Edit a flow component"
    ),
    keymap.Binding(
        "f",
        "view.setval.toggle @focus fullcontents",
        ["flowview"],
        "Toggle viewing full contents on this flow",
    ),
    keymap.Binding("w", "console.command save.file @focus ", ["flowview"], "Save flow to file"),
    keymap.Binding("space", "view.focus.next", ["flowview"], "Go to next flow"),

    keymap.Binding(
        "v",
        """
        console.choose "View Part" request,response
        console.bodyview @focus {choice}
        """,
        ["flowview"],
        "View flow body in an external viewer"
    ),
    keymap.Binding("p", "view.focus.prev", ["flowview"], "Go to previous flow"),
    keymap.Binding("m", "console.flowview.mode.set", ["flowview"], "Set flow view mode"),
    keymap.Binding(
        "z",
        """
        console.choose "Part" request,response
        flow.encode.toggle @focus {choice}
        """,
        ["flowview"],
        "Encode/decode flow body"
    ),

    keymap.Binding("L", "console.command options.load ", ["options"], "Load from file"),
    keymap.Binding("S", "console.command options.save ", ["options"], "Save to file"),
    keymap.Binding("D", "options.reset", ["options"], "Reset all options"),
    keymap.Binding("d", "console.options.reset.focus", ["options"], "Reset this option"),

    keymap.Binding("a", "console.grideditor.add", ["grideditor"], "Add a row after cursor"),
    keymap.Binding("A", "console.grideditor.insert", ["grideditor"], "Insert a row before cursor"),
    keymap.Binding("d", "console.grideditor.delete", ["grideditor"], "Delete this row"),
    keymap.Binding(
        "r",
        "console.command console.grideditor.readfile",
        ["grideditor"],
        "Read unescaped data from file"
    ),
    keymap.Binding(
        "R",
        "console.command console.grideditor.readfile_escaped",
        ["grideditor"],
        "Read a Python-style escaped string from file"
    ),
    keymap.Binding("e", "console.grideditor.editor", ["grideditor"], "Edit in external editor"),

    keymap.Binding("z", "console.eventlog.clear", ["eventlog"], "Clear"),

    keymap.Binding(
        "a",
        """
        console.choose.cmd "Context" console.key.contexts
        console.command console.key.bind {choice}
        """,
        ["keybindings"],
        "Add a key binding"
    ),
    keymap.Binding(
        "d",
        "console.key.unbind.focus",
        ["keybindings"],
        "Unbind the currently focused key binding"
    ),
    keymap.Binding(
        "x",
        "console.key.execute.focus",
        ["keybindings"],
        "Execute the currently focused key binding"
    ),
    keymap.Binding(
        "enter",
        "console.key.edit.focus",
        ["keybindings"],
        "Edit the currently focused key binding"
    ),
]
