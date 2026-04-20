from mcp_app import mcp

@mcp.resource("file://cleanup-report")
def cleanup_report() -> str:
    """A resource that returns a static summary of the disk state in the selected directories"""
    return "Cleanup report: Scan a directory to see candidates for deletion."