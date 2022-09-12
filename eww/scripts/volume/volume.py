import pulsectl
import subprocess

try:
    with pulsectl.Pulse('eww-volume') as pulse:
        sink = pulse.sink_list()[0]
        print("Listening to volume changes on ", sink.name)

        def print_event(_):
            raise pulsectl.PulseLoopStop

        pulse.event_mask_set('sink')
        pulse.event_callback_set(print_event)
        while True:
            command = f"volume_percent={round(pulse.sink_list()[0].volume.value_flat * 100.0)}"
            print("Running " + command)
            subprocess.run(["eww", "update", command])
            pulse.event_listen()
except Exception as e:
    print(e)
