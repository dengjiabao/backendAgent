import re


def rewrite_query(query: str) -> str:
    """移除礼貌性前缀，保留可用于检索的业务关键词。"""

    cleaned = re.sub(r"^(可以帮我|请帮我|帮我|麻烦|请)\s*", "", query.strip())
    return re.sub(r"(查询一下|查询|查一下|告诉我)", "", cleaned).strip()
