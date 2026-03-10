import subprocess
import json

def global_disks(request):
    try:
        result = subprocess.run(
            ["lsblk", "-o", "NAME,SIZE,TYPE,MOUNTPOINT", "-J"],
            stdout=subprocess.PIPE,
            text=True
        )
        data = json.loads(result.stdout)
        disks = [d for d in data["blockdevices"] if d["type"] == "disk"]
    except:
        disks = []

    return {"disks": disks}