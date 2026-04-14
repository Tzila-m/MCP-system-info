import psutil
import platform
import logging
from typing import Dict, Any
from models.system_model import SystemInfo

logger = logging.getLogger(__name__)

_MB = 1024**2
_GB = 1024**3

def get_system_info() -> Dict[str, Any]:
    logger.info("Fetching system information")
    net_io = psutil.net_io_counters()
    system_info = SystemInfo(
        system=platform.system(),
        node_name=platform.node(),
        release=platform.release(),
        version=platform.version(),
        machine=platform.machine(),
        processor=platform.processor(),
        cpu_cores=psutil.cpu_count(logical=False),
        logical_cpus=psutil.cpu_count(logical=True),
        ram=psutil.virtual_memory().total / _GB,
        disk_usage=psutil.disk_usage("/").percent,
        cpu_usage=psutil.cpu_percent(interval=0),
        memory_usage=psutil.virtual_memory().percent,
        network_sent=net_io.bytes_sent / _MB,
        network_recv=net_io.bytes_recv / _MB,
        uptime=psutil.boot_time(),
    )
    return system_info.to_dict()