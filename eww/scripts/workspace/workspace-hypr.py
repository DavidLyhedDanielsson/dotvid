import argparse
import socket
import os
import subprocess
import json
from typing import List, TypedDict

# Persistent storage for received event text
MESSAGE_BUFFER: str = ""


class HyprMonitorActiveWorkspace(TypedDict):
    id: int
    name: str


class HyprMonitor(TypedDict):
    id: int
    name: str
    width: int
    height: int
    refreshRate: float
    x: int
    y: int
    activeWorkspace: HyprMonitorActiveWorkspace
    reserved: List[int]
    scale: float
    transform: int
    focused: bool


class HyprWorkspaces(TypedDict):
    id: int
    name: int
    monitor: str
    windows: int
    hasfullscreen: bool
    lastwindow: str
    lastwindowtitle: str


class EwwWorkspace(TypedDict):
    id: int
    active: bool


def get_workspaces() -> EwwWorkspace:
    hypr_workspaces: List[HyprWorkspaces] = json.loads(subprocess.check_output(
        ["hyprctl", "-j", "workspaces"]))
    hypr_monitors: List[HyprMonitor] = json.loads(subprocess.check_output(
        ["hyprctl", "-j", "monitors"]))

    params: List[EwwWorkspace] = []

    for workspace in hypr_workspaces:
        params.append({
            "id": workspace["id"],
            "active": is_workspace_active(workspace["id"], hypr_monitors)
        })

    params.sort(key=lambda val: val["id"])

    return params


def is_workspace_active(workspace_id: int, monitors: List[HyprMonitor]) -> bool:
    for monitor in monitors:
        if monitor["activeWorkspace"]["id"] == workspace_id:
            return True

    return False


def eww_update(params: EwwWorkspace):
    subprocess.run(
        ["eww", "update", f"workspaces={json.dumps(params)}"])


def recv_event(client):
    global MESSAGE_BUFFER

    if '\n' in MESSAGE_BUFFER:
        return

    data_chunks: list[str] = []
    while True:
        recv_data = client.recv(4096)
        data_chunks.append(recv_data)
        if b'\n' in recv_data:
            break

    MESSAGE_BUFFER = MESSAGE_BUFFER + "".join(
        map(lambda s: s.decode('utf-8'), data_chunks))


def get_event() -> str:
    global MESSAGE_BUFFER

    if '\n' not in MESSAGE_BUFFER:
        return ""

    messages = MESSAGE_BUFFER

    newline_at = messages.find('\n')
    message_data = messages[:newline_at]
    rest_data = messages[newline_at + 1:]

    MESSAGE_BUFFER = rest_data
    return message_data


def listen_for_events():
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
        hypr_signature = os.environ["HYPRLAND_INSTANCE_SIGNATURE"]
        client.connect(f'/tmp/hypr/{hypr_signature}/.socket2.sock')

        while True:
            try:
                recv_event(client)

                update_workspace = False
                message = get_event()
                while message != "":
                    event, data = message.split('>>', 1)

                    if event in ["createworkspace", "destroyworkspace", "workspace"]:
                        update_workspace = True

                    message = get_event()

                if update_workspace:
                    params = get_workspaces()
                    eww_update(params)

            except Exception as ex:
                print(ex)


def run():
    parser = argparse.ArgumentParser("Interface to Hyprland workspaces")
    parser.add_argument("--get", action="store_true")
    args = parser.parse_args()

    if args.get:
        params = get_workspaces()
        eww_update(params)
    else:
        listen_for_events()


if __name__ == "__main__":
    run()
