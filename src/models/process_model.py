from dataclasses import dataclass, asdict
from typing import Any, Dict, List

import psutil

_MB = 1024**2
THRESHOLD_MEMORY_MB = 500  

@dataclass(frozen=True)
class ProcessInfo:
    pid: int
    name: str
    status: str
    cpu_usage: float
    memory_usage: float

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the ProcessInfo object to a dictionary for further usage or embedding.
        """
        return asdict(self)


def create_process(pid: int) -> ProcessInfo:
    proc = psutil.Process(pid)
    return ProcessInfo(
        pid=proc.pid,
        name=proc.name(),
        status=proc.status(),
        cpu_usage=proc.cpu_percent(interval=0),
        memory_usage=proc.memory_info().rss / _MB,
    )

def get_processes(limit: int) -> List[ProcessInfo]:
    result: List[ProcessInfo] = []

    for proc in psutil.process_iter(["pid"]):
        try:
            result.append(create_process(proc.pid))
            if len(result) >= limit:
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return result

def check_high_resource_usage(memory_threshold_mb: float = THRESHOLD_MEMORY_MB) -> List[ProcessInfo]:
    high_usage: List[ProcessInfo] = []

    for proc in psutil.process_iter(["pid"]):
        try:
            proc_obj = psutil.Process(proc.info["pid"])
            memory_mb = proc_obj.memory_info().rss / _MB
            if memory_mb > memory_threshold_mb:
                high_usage.append(create_process(proc_obj.pid))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return high_usage


def terminate_process(pid: int) -> bool:
    try:
        proc = psutil.Process(pid)
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except psutil.TimeoutExpired:
            proc.kill()
        return True
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False