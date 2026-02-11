import data
from fastmcp import FastMCP

# MCP 서버 생성
mcp = FastMCP("Fashion Server")


@mcp.tool
def get_ootd(day: str) -> str:
    """Get the outfit of the day for a specific day of the week."""
    outfit = data.get_ootd(day)
    return outfit if outfit else "기록된 코디가 없습니다."


@mcp.tool
def get_all_members() -> list[str]:
    """Get the list of all team member usernames."""
    return data.get_all_members()


@mcp.tool
def get_member_detail(username: str) -> dict | str:
    """Get detailed profile information including location and style for a team member.
    Returns error message if member is not found.
    """
    member = data.get_member(username)
    if not member:
        return "팀원을 찾을 수 없습니다."
    return member


if __name__ == "__main__":
    mcp.run()
