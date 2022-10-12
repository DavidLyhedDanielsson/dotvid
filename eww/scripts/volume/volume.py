from email.policy import default
import pulsectl
import subprocess


def get_default_sink(pulse):
    default_sink_name = pulse.server_info().default_sink_name

    for potential_sink in pulse.sink_list():
        if potential_sink.name == default_sink_name:
            return potential_sink

    return None


try:
    with pulsectl.Pulse('eww-volume') as pulse:
        sink = get_default_sink(pulse)
        if not sink:
            print("No default sink available")
            exit(-1)

        print("Listening to volume changes on ", sink.name)

        def print_event(e):
            raise pulsectl.PulseLoopStop

        pulse.event_mask_set('sink')
        pulse.event_callback_set(print_event)
        while True:
            command = f"volume_percent={round(get_default_sink(pulse).volume.value_flat * 100.0)}"
            print("Running " + command)
            subprocess.run(["eww", "update", command])
            pulse.event_listen()
except Exception as e:
    print(e)
