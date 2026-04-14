# @mcp.tool(description="Terminate a process after validation and user confirmation")
# def terminate_process_tool(pid: int, confirmed: bool):

#     if not confirmed:
#         return {"success": False, "message": "User confirmation required", "pid": pid}
#     return process_service.terminate_process_with_validation(pid)


# @mcp.tool(description="Return the first 20 running processes in the system")
# def list_processes_tool(number: int = 30):
#     return process_service.get_processes(number)


# @mcp.tool(
#     description="This tool checks for processes consuming excessive resources and suggests closing them."
# )
# def resource_usage_tool():
#     return process_service.get_high_resource_usage()