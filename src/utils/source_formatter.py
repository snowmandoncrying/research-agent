

# 검색 결과를 LLM이 읽을 수 있는 형태로 번역
def format_sources(search_results: list[dict]) -> str:
    return "\n\n".join([
      f"[{i+1}] {result.get('title', 'No Title')}\n"
      f"URL: {result.get('url', 'N/A')}\n"
      f"{result.get('content', '')[:300]}..."
      for i, result in enumerate(search_results)
    ])