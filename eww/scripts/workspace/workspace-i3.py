#!/usr/bin/env python3
# pylint: disable=missing-class-docstring, missing-function-docstring

import argparse
from curses.ascii import isdigit, isspace
from dataclasses import dataclass
from functools import cmp_to_key, reduce
from locale import currency
from i3ipc import Connection, Event
import subprocess
import json
from typing import TypedDict

WINDOW_ICONS = {
    'alacritty': '',
    'code': '',
    'discord': 'ﭮ',
    'firefox': '',
    'pavucontrol': '',
    'spotify': '',  # could also use the 'spotify' icon
    'zoom': '',
}


def get_workspace_icons(name: str) -> list[str]:
    return [*name] if ":" not in name else list(filter(lambda x: not isspace(x), [*(name.split(":", 1)[1])]))


def get_workspace_number(name: str, default: int = -1) -> int:
    if ":" not in name:
        return int(name)

    potential = name.split(":", 1)[0]

    if all(map(lambda x: isdigit(x) or isspace(x), potential)):
        return int(potential)
    else:
        return default


class EwwData(TypedDict):
    id: str
    name: str
    active: bool


@dataclass
class Window:
    wclass: str
    focused: bool


@dataclass
class Workspace:
    output: str
    # Must keep this around to be able to rename it
    current_name: str
    number: int
    icons: list[str]

    focused: bool
    visible: bool
    windows: list[Window]


def compare_workspace(lhs: Workspace, rhs: Workspace):
    # compare numbers?
    if lhs.output.startswith("edp"):
        if lhs.output != rhs.output:
            return -1

        return lhs.number - rhs.number
    if rhs.output.startswith("edp"):
        return 1

    if lhs.output < rhs.output:
        return -1
    elif lhs.output == rhs.output:
        return 0
    else:
        return 1


def get_all_workspaces(i3: Connection) -> list[Workspace]:
    data: list[Workspace] = []

    workspace_visibility = {x.name: x.visible for x in i3.get_workspaces()}

    for workspace in i3.get_tree().workspaces():
        output: str = workspace.ipc_data["output"].lower()
        name: str = workspace.name  # pyright: ignore
        windows: list[Window] = [Window(leaf.window_class.lower(), leaf.focused)  # pyright: ignore
                                 for leaf in workspace.leaves()]
        focused: bool = workspace.focused or reduce(  # pyright: ignore
            lambda v, w: (v or w.focused), windows, False)
        visible: bool = workspace_visibility[name]

        data.append(Workspace(output, name, get_workspace_number(
            name), get_workspace_icons(name), focused, visible, windows))

    # Keep integrated monitor first
    return list(sorted(data, key=cmp_to_key(compare_workspace)))


def get_active_output(i3: Connection) -> str | None:
    for workspace in i3.get_tree().workspaces():
        if workspace.focused:  # type: ignore
            return workspace.ipc_data["output"].lower()  # type: ignore

        for leaf in workspace.leaves():
            if leaf.focused:  # type: ignore
                return workspace.ipc_data["output"].lower()  # type: ignore

    return None


def rename_all(tup: tuple[int, Workspace]) -> Workspace:
    number, workspace = tup

    focused: bool = workspace.focused
    icons: list[str] = []
    for window in workspace.windows:
        focused = focused or window.focused

        if window.wclass in WINDOW_ICONS:
            icons.append(WINDOW_ICONS[window.wclass])
        else:
            icons.append("??")

    return Workspace(workspace.output, workspace.current_name, number + 1, icons, focused, workspace.visible, workspace.windows)


def remove_empty(workspace: Workspace) -> Workspace | None:
    return None if len(workspace.icons) == 0 else workspace


def submit_i3_data(i3: Connection, workspaces: list[Workspace]):
    for workspace in reversed(workspaces):
        if workspace.current_name != str(workspace.number):
            i3.command(
                f"rename workspace \"{workspace.current_name}\" to \"{workspace.number}\"")

    for workspace in workspaces:
        if workspace.current_name == "":
            i3.command(f"workspace {workspace.number}")


def submit_eww_data(data: list[Workspace]):
    #     {
    #         'id': f"{str(counter)}:",
    #         'name': "".join(icons),
    #         'active': focused_workspace
    #     })

    eww_data = list(map(lambda w: {
        'id': f"{str(w.number)}:",
        'name': "".join(w.icons),
        'active': w.visible
    }, data))

    subprocess.run(
        ["eww", "update", f"workspaces={json.dumps(eww_data)}"])


def get_last_visible_on_output(workspaces: list[Workspace], output: str) -> int:
    found_visible: bool = False
    for (i, w) in enumerate(workspaces):
        found_visible = found_visible or (
            w.visible and w.output == output)
        if found_visible and w.output != output:
            return i - 1

    return len(workspaces) - 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n",
                        action="store_true",
                        help="create a new workspace on the current monitor")
    parser.add_argument("-m",
                        action="store_true",
                        help="move current window to a new workpace on the current monitor")
    parser.add_argument("-d",
                        action="store_true",
                        help="daemon")

    args = parser.parse_args()
    if not args.d and not args.n and not args.m:
        #args.d = True
        args.n = True
        #args.m = True

    i3 = Connection()
    if args.n:
        active_monitor = get_active_output(i3)
        if not active_monitor:
            exit(1)

        workspaces: list[Workspace] = get_all_workspaces(i3)

        last_visible = get_last_visible_on_output(workspaces, active_monitor)

        workspaces.insert(last_visible + 1, Workspace(
            active_monitor, "", workspaces[last_visible].number + 1, [], True, True, []))

        for i in range(last_visible + 2, len(workspaces)):
            workspaces[i].number += 1

        submit_i3_data(i3, workspaces)
    elif args.m:
        active_monitor = get_active_output(i3)
        if not active_monitor:
            exit(1)

        workspaces: list[Workspace] = get_all_workspaces(i3)

        last_visible = get_last_visible_on_output(
            workspaces, active_monitor)

        for i in range(last_visible + 1, len(workspaces)):
            workspaces[i].number += 1

        submit_i3_data(i3, workspaces)
        i3.command(
            f"move window to workspace {workspaces[last_visible].number + 1}")
        i3.command(f"workspace {workspaces[last_visible].number + 1}")
    elif args.d:
        doing_stuff: bool = False

        # Rename at startup to valid workspace names
        def do_rename():
            nonlocal doing_stuff
            if doing_stuff:
                print("doing_stuff is true")
                return

            doing_stuff = True

            data: list[Workspace] = list(
                map(rename_all, enumerate(get_all_workspaces(i3))))

            submit_eww_data(data)
            submit_i3_data(i3, data)

            doing_stuff = False

        do_rename()
        i3.on(Event.WINDOW_NEW, lambda i3, event: do_rename())
        i3.on(Event.WINDOW_CLOSE, lambda i3, event: do_rename())
        i3.on(Event.WINDOW_MOVE, lambda i3, event: do_rename())
        i3.on(Event.WORKSPACE_FOCUS, lambda i3, event: do_rename())
        i3.on(Event.WORKSPACE_INIT, lambda i3, event: do_rename())
        i3.main()


if __name__ == "__main__":
    main()
