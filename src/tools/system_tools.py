from mcp_app import mcp
from services import system_services

@mcp.tool(
    description="This tool returns system information like CPU, RAM, Disk usage, etc."
)
def system_info_tool():
    return system_services.get_system_info()


