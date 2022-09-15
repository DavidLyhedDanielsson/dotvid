import time
import psutil
import subprocess
import json

new_data = False

prev_usage = psutil.cpu_percent(percpu=True)
usages = psutil.cpu_percent(interval=1, percpu=True)

steps_to_update = 15
time_to_update = 0.5
sleep_time = 1

while True:
    usages = psutil.cpu_percent(interval=None, percpu=True)

    long_sleep = True

    params = [0] * len(usages)
    for (i, usage) in enumerate(usages):
        diff = (usage - prev_usage[i])
        params[i] = round(prev_usage[i] + diff)

        if abs(diff) > 25:
            long_sleep = False

    subprocess.run(
        ["eww", "update", f"cores={json.dumps(params)}"])

    prev_usage = usages
    time.sleep(1 if long_sleep else 0.1)
