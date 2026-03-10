from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import subprocess
import psutil
import json
import os
import pyinotify

# ------------------------
# États globaux
# ------------------------
monitoring_status = {}        # disque: True/False
disk_last_counters = {}       # disque: {"r":..., "w":...}
disk_file_snapshots = {}      # disque: liste de fichiers récents
disk_watchers = {}            # disque: notifier pyinotify

# ------------------------
# Pages
# ------------------------
def index(request):
    return render(request, "monitoring/index.html")

def login(request):
    return render(request, "monitoring/signin.html")

def home(request):
    try:
        result = subprocess.run(
            ["lsblk", "-o", "NAME,SIZE,TYPE,MOUNTPOINT", "-J"],
            stdout=subprocess.PIPE, text=True, check=True
        )
        data = json.loads(result.stdout)
    except Exception:
        data = {"blockdevices": []}

    disks = []
    for d in data.get("blockdevices", []):
        if d["type"] == "disk":
            disks.append({
                "name": d["name"],
                "size": d["size"],
                "children": d.get("children") or []
            })

    return render(request, "monitoring/home.html", {"disks": disks})

# ------------------------
# Récupérer tous les points de montage
# ------------------------
def get_mount_points(disk_name):
    try:
        result = subprocess.run(
            ["lsblk", "-o", "NAME,MOUNTPOINT", "-J", f"/dev/{disk_name}"],
            stdout=subprocess.PIPE, text=True, check=True
        )
        data = json.loads(result.stdout)
        mounts = []

        def extract(dev):
            if dev.get("mountpoint") and dev["mountpoint"] != "[SWAP]":
                mounts.append(dev["mountpoint"])
            for child in dev.get("children", []):
                extract(child)

        for dev in data.get("blockdevices", []):
            extract(dev)
        return mounts
    except Exception:
        return []

# ------------------------
# Pyinotify Handler
# ------------------------
class DiskEventHandler(pyinotify.ProcessEvent):
    def __init__(self, disk_name):
        self.disk_name = disk_name
        super().__init__()

    def process_IN_CREATE(self, event):
        path = event.pathname
        try:
            size = os.path.getsize(path) // 1024 if os.path.exists(path) else 0
        except:
            size = 0
        disk_file_snapshots[self.disk_name].append({"path": path, "size_kb": size, "type": "W"})
        # garder seulement les 50 derniers fichiers pour ne pas saturer
        if len(disk_file_snapshots[self.disk_name]) > 50:
            disk_file_snapshots[self.disk_name] = disk_file_snapshots[self.disk_name][-50:]

    def process_IN_MODIFY(self, event):
        path = event.pathname
        try:
            size = os.path.getsize(path) // 1024 if os.path.exists(path) else 0
        except:
            size = 0
        disk_file_snapshots[self.disk_name].append({"path": path, "size_kb": size, "type": "R"})
        if len(disk_file_snapshots[self.disk_name]) > 50:
            disk_file_snapshots[self.disk_name] = disk_file_snapshots[self.disk_name][-50:]

# ------------------------
# Démarrer / arrêter le monitoring
# ------------------------
@csrf_exempt
def start_disk(request, disk_name):
    mounts = get_mount_points(disk_name)
    if not mounts:
        return JsonResponse({"message": f"Disque {disk_name} inexistant ou non monté"})

    monitoring_status[disk_name] = True
    disk_file_snapshots.setdefault(disk_name, [])

    # démarrage pyinotify
    wm = pyinotify.WatchManager()
    mask = pyinotify.IN_CREATE | pyinotify.IN_MODIFY
    handler = DiskEventHandler(disk_name)
    notifier = pyinotify.ThreadedNotifier(wm, handler)
    notifier.start()
    for mount in mounts:
        wm.add_watch(mount, mask, rec=True)
    disk_watchers[disk_name] = notifier

    return JsonResponse({"message": f"Monitoring démarré ({disk_name})"})

@csrf_exempt
def stop_disk(request, disk_name):
    monitoring_status[disk_name] = False
    # arrêt pyinotify
    if disk_name in disk_watchers:
        disk_watchers[disk_name].stop()
        del disk_watchers[disk_name]
    return JsonResponse({"message": f"Monitoring arrêté ({disk_name})"})

# ------------------------
# Stats I/O
# ------------------------
def disk_stats(request, disk_name):
    io = psutil.disk_io_counters(perdisk=True)
    if disk_name not in io:
        return JsonResponse({"error": "Introuvable"}, status=404)

    c = io[disk_name]
    last = disk_last_counters.get(disk_name, {"r": 0, "w": 0})
    read_delta = c.read_bytes - last["r"]
    write_delta = c.write_bytes - last["w"]
    disk_last_counters[disk_name] = {"r": c.read_bytes, "w": c.write_bytes}

    return JsonResponse({
        "read_kb": round(read_delta / 1024, 2),
        "write_kb": round(write_delta / 1024, 2)
    })

# ------------------------
# Usage disque
# ------------------------
def disk_usage(request, disk_name):
    mounts = get_mount_points(disk_name)
    if not mounts:
        return JsonResponse({"total": "0", "used": "0", "free": "0", "percent": 0})

    usage = psutil.disk_usage(mounts[0])
    return JsonResponse({
        "total": f"{usage.total/1024/1024/1024:.2f} GB",
        "used": f"{usage.used/1024/1024/1024:.2f} GB",
        "free": f"{usage.free/1024/1024/1024:.2f} GB",
        "percent": usage.percent
    })

# ------------------------
# Fichiers ouverts / créés (15 plus récents)
# ------------------------
@csrf_exempt
def disk_open_files(request, disk_name):
    if not monitoring_status.get(disk_name):
        return JsonResponse({"files": []})

    # prendre les 15 derniers fichiers
    recent_files = disk_file_snapshots.get(disk_name, [])[-15:]

    # renommer 'type' en 'action' pour le front-end
    files = [
        {"path": f["path"], "size_kb": f["size_kb"], "action": f["type"]}
        for f in recent_files
    ]

    return JsonResponse({"files": files})