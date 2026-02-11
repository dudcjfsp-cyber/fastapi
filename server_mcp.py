from mcp.server.fastmcp import FastMCP
import data

# MCP 서버 생성
mcp = FastMCP("Fashion Agent", dependencies=["fastapi", "uvicorn"])


# ──────────────────────────────────────────────
# Resource & Tool: 팀원 명부
# ──────────────────────────────────────────────
@mcp.resource("fashion://members")
def get_members() -> str:
    """팀원 전체 목록을 텍스트로 반환합니다."""
    result = "=== 팀원 목록 ===\n"
    # get_all_members()가 이미 전체 정보를 반환하므로 재조회 불필요
    for m in data.get_all_members():
        result += f"- {m['name']} ({m['username']}): {m['location']}, {m['style']}\n"
    return result


@mcp.tool()
def list_team_members() -> str:
    """팀원 전체 목록을 조회합니다."""
    return get_members()


@mcp.resource("fashion://members/{username}")
def get_member_profile(username: str) -> str:
    """특정 팀원의 상세 정보를 반환합니다."""
    member = data.get_member(username)
    if not member:
        return "존재하지 않는 팀원입니다."
    return f"""\
이름: {member['name']}
성별: {member['gender']}
스타일: {member['style']}
위치: {member['location']}
"""


@mcp.tool()
def get_member_info(username: str) -> str:
    """(username)을 입력받아 팀원의 상세 정보를 조회합니다."""
    return get_member_profile(username)


# ──────────────────────────────────────────────
# Tool: 코디 로그 조회
# ──────────────────────────────────────────────
@mcp.tool()
def get_outfit_log(day: str) -> str:
    """특정 요일의 옷차림 기록을 조회합니다."""
    outfit = data.get_ootd(day)
    return outfit if outfit else "기록된 코디가 없습니다."


# ──────────────────────────────────────────────
# Prompt: 패션 추천 요청
# ──────────────────────────────────────────────
@mcp.prompt()
def recommend_fashion(username: str) -> str:
    """특정 팀원을 위한 패션 추천 프롬프트를 생성합니다."""
    member = data.get_member(username)
    if not member:
        return "존재하지 않는 팀원입니다."

    return f"""\
당신은 최고의 AI 패션 스타일리스입니다.
다음 팀원의 정보를 바탕으로, 현재 날씨(별도 조회 필요)에 맞는 옷차림을 추천해주세요.

대상: {member['name']} ({member['gender']})
선호 스타일: {member['style']}
지 역: {member['location']}

1. 먼저 해당 지역({member['location']})의 오늘 날씨를 검색하세요.
2. 그 날씨와 선호 스타일({member['style']})을 고려하여 구체적인 코디를 제안해주세요.
"""


if __name__ == "__main__":
    mcp.run()
