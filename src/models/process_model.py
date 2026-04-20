from dataclasses import dataclass, asdict
from typing import Any, Dict, List

import psutil


BYTES_TO_MB = 1024 ** 2
THRESHOLD_MEMORY_MB = 500
TERMINATION_TIMEOUT_SEC = 3
IGNORED_EXCEPTIONS = (psutil.NoSuchProcess, psutil.AccessDenied)



@dataclass(frozen=True)
class ProcessInfo:
    pid: int
    name: str
    status: str
    cpu_usage: float
    memory_usage: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# =======================
# Mapping & Fetching
# =======================

def fetch_process(pid: int) -> psutil.Process:
    return psutil.Process(pid)


def map_to_process_info(proc: psutil.Process) -> ProcessInfo:
    return ProcessInfo(
        pid=proc.pid,
        name=proc.name(),
        status=proc.status(),
        cpu_usage=proc.cpu_percent(interval=0),
        memory_usage=proc.memory_info().rss / BYTES_TO_MB,
    )


def create_process(pid: int) -> ProcessInfo:
    proc = fetch_process(pid)
    return map_to_process_info(proc)


# =======================
# Core Functions
# =======================

def get_processes(limit: int) -> List[ProcessInfo]:
    result: List[ProcessInfo] = []

    for proc in psutil.process_iter():
        try:
            result.append(create_process(proc.pid))
            if len(result) >= limit:
                break
        except IGNORED_EXCEPTIONS:
            continue

    return result


def is_high_memory(proc: psutil.Process, threshold: float) -> bool:
    return (proc.memory_info().rss / BYTES_TO_MB) > threshold


def check_high_resource_usage(memory_threshold_mb: float = THRESHOLD_MEMORY_MB) -> List[ProcessInfo]:
    high_usage: List[ProcessInfo] = []

    for proc in psutil.process_iter():
        try:
            if is_high_memory(proc, memory_threshold_mb):
                high_usage.append(map_to_process_info(proc))
        except IGNORED_EXCEPTIONS:
            continue

    return high_usage


def get_root_parent(pid: int) -> psutil.Process | None:
    try:
        proc = fetch_process(pid)
        name = proc.name()
        current = proc

        while True:
            parent = current.parent()
            if parent is None:
                return current

            try:
                if parent.name() != name:
                    return current
            except IGNORED_EXCEPTIONS:
                return current

            current = parent
    except (psutil.Error, *IGNORED_EXCEPTIONS):
        return None


# =======================
# Termination Logic (Refactored)
# =======================

def collect_process_tree(proc: psutil.Process) -> List[psutil.Process]:
    processes = proc.children(recursive=True)
    processes.append(proc)
    return processes


def terminate_processes(processes: List[psutil.Process]) -> None:
    for process in processes:
        try:
            process.terminate()
        except IGNORED_EXCEPTIONS:
            continue


def kill_remaining_processes(processes: List[psutil.Process]) -> None:
    _, alive = psutil.wait_procs(processes, timeout=TERMINATION_TIMEOUT_SEC)

    for process in alive:
        try:
            process.kill()
        except IGNORED_EXCEPTIONS:
            continue


def terminate_process(pid: int) -> bool:
    try:
        root_proc = get_root_parent(pid)
        if root_proc is None:
            return False

        processes_to_stop = collect_process_tree(root_proc)

        terminate_processes(processes_to_stop)
        kill_remaining_processes(processes_to_stop)

        return not psutil.pid_exists(pid)

    except (psutil.Error, *IGNORED_EXCEPTIONS):
        return False