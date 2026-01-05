from src.nodes.report_generator import generate_report
from src.nodes.report_reviewer import review_report

print("="*60)
print("리포트 생성 및 리뷰 시스템 테스트")
print("="*60)

# ========== 1. 초기 리포트 생성 ==========
print("\n[1단계] 초기 리포트 생성")

mock_state = {
    "topic": "AI 기술 트렌드 2025",
    "search_results": [
        {"title": "GPT-5 전망", "url": "https://test.com/1", "content": "GPT-5는 2025년 출시 예정..."},
        {"title": "AI 시장 성장", "url": "https://test.com/2", "content": "AI 시장은 연 30% 성장..."},
    ],
    "revision_count": 0,
    "review_status": None,  # ✅ 첫 생성
    "final_report": None,
    "review_feedback": None
}

gen_result = generate_report(mock_state)
mock_state.update(gen_result)

print(f"[완료] 생성 완료")
print(f"리포트 길이: {len(mock_state['final_report'])}자")
print(f"파일 저장: {mock_state.get('output_path')}")  # None이어야 함
print(f"미리보기:\n{mock_state['final_report'][:200]}...\n")

# ========== 2. 첫 번째 리뷰 ==========
print("\n[2단계] 리포트 리뷰")

rev_result = review_report(mock_state)
mock_state.update(rev_result)

print(f"리뷰 상태: {mock_state['review_status']}")
print(f"수정 횟수: {mock_state['revision_count']}")
print(f"피드백: {mock_state.get('review_feedback', 'None')}\n")

# ========== 3. 분기 처리 ==========
if mock_state["review_status"] == "needs_revision":
    print("\n[3단계] 수정 후 재생성")
    
    # 다시 생성 (피드백 반영)
    gen_result = generate_report(mock_state)
    mock_state.update(gen_result)
    
    print(f"[완료] 수정 완료")
    print(f"수정된 리포트 미리보기:\n{mock_state['final_report'][:200]}...\n")
    
    # 다시 리뷰
    print("\n[4단계] 재리뷰")
    rev_result = review_report(mock_state)
    mock_state.update(rev_result)
    
    print(f"리뷰 상태: {mock_state['review_status']}")
    print(f"수정 횟수: {mock_state['revision_count']}")

# ========== 4. 최종 승인 시 ==========
if mock_state["review_status"] == "approved":
    print("\n[최종] 승인 → 파일 생성")
    
    # 다시 호출해서 파일 저장
    final_result = generate_report(mock_state)
    mock_state.update(final_result)
    
    print(f"[완료] 최종 파일 저장 완료")
    print(f"파일 경로: {mock_state.get('output_path')}")

print("\n" + "="*60)
print("테스트 완료!")
print(f"최종 상태: {mock_state['review_status']}")
print(f"총 수정 횟수: {mock_state['revision_count']}")
print("="*60)