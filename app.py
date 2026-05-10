import os
from datetime import datetime

import requests
import streamlit as st


DEFAULT_INPUT = """엑셀로 거래처별 주문 내역을 정리해야 하는데,
중복된 행이나 누락된 값이 있는지 확인하는 데 시간이 오래 걸립니다.
직장인이 AI에게 어떻게 부탁하면 빠르게 정리할 수 있는지 쇼츠 영상으로 만들고 싶습니다."""

DEFAULT_REPORT_INPUT = """2026년 직장인들이 업무에 AI를 활용하는 최신 사례를 찾아서
사무직이 바로 따라 할 수 있는 방식으로 정리해주세요.

특히 문서 정리, 보고서 작성, 엑셀 업무, 자료 조사에 도움이 되는 사례가 필요합니다."""

DEFAULT_WORK_INPUT = """거래처별 주문 내역 엑셀 파일에서
중복 주문, 누락된 수량, 비어 있는 금액을 찾아서 정리하고 싶습니다.

AI를 어떻게 활용하면 이 업무를 빠르게 처리할 수 있는지
순서대로 알려주세요."""

POPULAR_OFFICE_AI_TASKS = [
    {
        "title": "엑셀 중복/누락 찾기",
        "text": "엑셀 파일에서 중복된 행, 비어 있는 값, 이상한 숫자를 찾아 정리하고 싶습니다. AI를 활용해서 빠르게 검수하고 표로 정리하는 방법을 알려주세요.",
    },
    {
        "title": "회의록 요약",
        "text": "회의록이나 녹취 내용을 보고 핵심 결정사항, 담당자별 할 일, 마감일을 정리하고 싶습니다. AI로 회의 내용을 업무용 요약본으로 만드는 방법을 알려주세요.",
    },
    {
        "title": "보고서 초안 작성",
        "text": "흩어져 있는 자료를 바탕으로 업무 보고서 초안을 작성하고 싶습니다. AI에게 어떤 순서로 자료를 주고 보고서 구조를 만들게 하면 좋을지 알려주세요.",
    },
    {
        "title": "거래처 이메일 작성",
        "text": "거래처에 보낼 정중한 이메일을 빠르게 작성하고 싶습니다. 상황과 요청사항만 넣으면 AI가 이메일 초안을 만들 수 있게 방법과 프롬프트를 알려주세요.",
    },
    {
        "title": "자료 조사/비교 정리",
        "text": "특정 주제에 대한 자료를 검색해서 핵심 내용, 장단점, 비교표로 정리하고 싶습니다. AI를 활용해 신뢰도 있는 자료를 찾고 정리하는 방법을 알려주세요.",
    },
    {
        "title": "문서 오탈자/누락 검수",
        "text": "계약서, 제안서, 안내문 같은 문서에서 오탈자, 빠진 항목, 앞뒤가 맞지 않는 내용을 찾고 싶습니다. AI로 문서를 검수하는 방법을 알려주세요.",
    },
    {
        "title": "기획안 아이디어 정리",
        "text": "새로운 이벤트, 콘텐츠, 상품 기획 아이디어를 정리하고 싶습니다. AI를 활용해 아이디어를 뽑고 실행 가능한 기획안으로 정리하는 방법을 알려주세요.",
    },
    {
        "title": "고객 문의 답변 초안",
        "text": "고객 문의 내용을 보고 친절하고 정확한 답변 초안을 만들고 싶습니다. AI가 답변을 작성하되 사람이 확인해야 할 부분까지 구분하는 방법을 알려주세요.",
    },
    {
        "title": "재고/주문 현황 정리",
        "text": "제품별 재고, 주문 수량, 부족한 품목을 정리하고 싶습니다. 엑셀 데이터를 AI로 분석해서 확인해야 할 항목을 뽑는 방법을 알려주세요.",
    },
    {
        "title": "긴 글 핵심 요약",
        "text": "긴 기사, 보고서, 공지문을 읽고 핵심 요약, 해야 할 일, 중요한 숫자만 빠르게 정리하고 싶습니다. AI로 업무용 요약문을 만드는 방법을 알려주세요.",
    },
]

ROLE_TASKS = {
    "비서실": [
        ("회의록 요약 + 액션아이템", "회의록이나 회의 메모를 넣으면 핵심 논의 내용, 결정사항, 담당자별 액션아이템, 마감일을 표로 정리하고 싶습니다."),
        ("대표 보고 브리핑 1페이지", "여러 자료나 긴 문서를 넣으면 대표 보고용으로 핵심 요약, 주요 이슈, 의사결정 필요사항을 1페이지 브리핑 형태로 정리하고 싶습니다."),
        ("일정 조율 메일", "미팅 후보 일정과 참석자 상황을 넣으면 일정 조율용 메일 초안, 회신 후보 문구, 확정 안내문을 만들고 싶습니다."),
        ("출장/방문 의전 체크리스트", "출장이나 외부 손님 방문 정보를 넣으면 일정표, 준비물, 동선, 의전 체크리스트를 자동으로 작성하고 싶습니다."),
        ("회의 전 사전자료 요약", "회의 전에 읽어야 할 자료를 넣으면 참석자가 빠르게 이해할 수 있는 사전 요약본과 확인 질문을 만들고 싶습니다."),
        ("긴 메일 보고용 재작성", "긴 이메일 내용을 넣으면 상사에게 보고하기 좋은 톤으로 핵심만 요약하고, 필요한 대응안을 정리하고 싶습니다."),
        ("주간 일정 우선순위 정리", "주간 일정 목록을 넣으면 중요도와 긴급도에 따라 우선순위를 나누고, 오늘 먼저 처리할 일을 정리하고 싶습니다."),
    ],
    "경영지원/총무": [
        ("사내 공지문 초안", "공지해야 할 내용을 넣으면 직원들이 이해하기 쉬운 사내 공지문 초안을 제목, 본문, 유의사항 형식으로 작성하고 싶습니다."),
        ("사내 규정/복지 쉬운 말 요약", "사내 규정이나 복지 제도 문서를 넣으면 직원들이 이해하기 쉬운 말로 핵심 내용, 적용 대상, 주의사항을 요약하고 싶습니다."),
        ("영수증 항목 분류표", "영수증 사진이나 비용 내역을 넣으면 날짜, 사용처, 금액, 비용 항목, 확인 필요 여부로 분류표를 만들고 싶습니다."),
        ("비용 정산 누락/중복 체크", "비용 정산 내역을 넣으면 누락된 항목, 중복된 항목, 금액 이상 항목을 찾아 표로 정리하고 싶습니다."),
        ("비품 구매 요청 표 정리", "비품 구매 요청 내용을 넣으면 품목, 수량, 예상 금액, 요청 부서, 우선순위별 표로 정리하고 싶습니다."),
        ("계약서 필수 항목 체크", "계약서 내용을 넣으면 계약 기간, 금액, 지급 조건, 해지 조건, 서명란 등 필수 항목 누락 여부를 체크리스트로 확인하고 싶습니다."),
        ("자산관리대장 표준화", "자산관리대장 데이터를 넣으면 자산명, 관리번호, 위치, 담당자, 상태 값을 표준화하고 누락된 값을 찾고 싶습니다."),
        ("월간 총무 보고 요약", "한 달 동안의 총무 업무 내역을 넣으면 주요 처리사항, 비용, 이슈, 다음 달 할 일을 보고용 요약문으로 만들고 싶습니다."),
    ],
    "영업지원": [
        ("거래처별 이메일 초안", "거래처 상황과 요청사항을 넣으면 정중한 이메일 초안을 작성하고, 거래처별 톤을 유지하는 방법까지 알고 싶습니다."),
        ("견적 요청 메일", "견적 요청 상황을 넣으면 신규 문의, 재견적 요청, 가격 조정 요청 등 상황별 견적 요청 메일을 빠르게 작성하고 싶습니다."),
        ("발주서/주문서 표 정리", "발주서나 주문서 내용을 넣으면 거래처, 상품명, 수량, 단가, 납기일, 확인 필요 항목을 표로 정리하고 싶습니다."),
        ("고객 문의 답변 초안", "고객 문의 내용을 넣으면 친절한 답변 초안을 만들고, 사람이 확인해야 할 금액/일정/정책 부분을 따로 표시하고 싶습니다."),
        ("영업 실적 주간 보고", "영업 실적과 활동 메모를 넣으면 주간 보고용으로 성과, 이슈, 다음 액션을 정리하고 싶습니다."),
        ("거래처별 진행현황 표", "거래처별 미팅, 견적, 계약, 납품 진행 상황을 넣으면 단계별 현황표와 확인할 일을 만들고 싶습니다."),
        ("미응답 고객 팔로업", "미응답 고객 리스트를 넣으면 우선순위를 정하고, 다시 연락할 팔로업 문구를 상황별로 만들고 싶습니다."),
        ("회의 후 후속조치 메일", "거래처 회의 메모를 넣으면 감사 인사, 결정사항, 후속 요청, 일정 확인이 포함된 메일을 작성하고 싶습니다."),
    ],
    "온라인 쇼핑몰 운영": [
        ("CS 답변 초안", "배송, 교환, 반품, 상품 문의 내용을 넣으면 고객에게 보낼 친절한 CS 답변 초안을 만들고 싶습니다."),
        ("리뷰 감성 분석", "상품 리뷰를 넣으면 긍정 리뷰, 부정 리뷰, 반복 불만, 개선 포인트를 분류하고 요약하고 싶습니다."),
        ("상품명/옵션명 표준화", "상품명과 옵션명을 넣으면 고객이 이해하기 쉬운 표준 상품명, 옵션명, 옵션 그룹으로 정리하고 싶습니다."),
        ("주문/재고 현황 요약", "주문 내역과 재고표를 넣으면 부족한 품목, 과잉 재고, 중복 주문, 확인 필요한 항목을 요약하고 싶습니다."),
        ("상품 상세설명 초안", "상품 특징과 스펙을 넣으면 쇼핑몰 상세설명 초안을 고객이 이해하기 쉬운 문장으로 작성하고 싶습니다."),
        ("반품/교환 안내문", "반품이나 교환 정책을 넣으면 고객에게 안내할 수 있는 쉽고 정중한 안내문을 만들고 싶습니다."),
        ("FAQ 자동 응답 문구", "자주 묻는 질문과 답변 기준을 넣으면 쇼핑몰 고객 응대용 FAQ 답변 문구를 만들고 싶습니다."),
        ("경쟁사 상품 비교표", "경쟁사 상품 정보를 검색하거나 입력하면 가격, 구성, 장점, 차별점을 비교표로 정리하고 싶습니다."),
    ],
    "상세페이지/마케팅 보조": [
        ("상세페이지 구성안", "상품 정보를 넣으면 상세페이지 섹션 순서, 제목, 핵심 문구, 이미지에 들어갈 내용을 구성하고 싶습니다."),
        ("상품 USP 추출", "상품 특징과 고객 리뷰를 넣으면 고객이 구매해야 할 핵심 장점 3~5개를 뽑고 소구점으로 정리하고 싶습니다."),
        ("카피 문구 대량 생성", "상품 정보를 넣으면 타이틀, 서브카피, 배너 문구, 버튼 문구를 여러 버전으로 만들고 싶습니다."),
        ("리뷰 기반 소구점", "고객 리뷰를 넣으면 반복적으로 언급되는 만족 포인트와 불만 포인트를 정리해 마케팅 문구로 바꾸고 싶습니다."),
        ("광고 후킹 문구", "상품이나 서비스 정보를 넣으면 SNS 광고, 배너, 쇼츠 첫 문장에 쓸 후킹 문구를 여러 버전으로 만들고 싶습니다."),
        ("경쟁상품 차별점 표", "경쟁상품 정보를 넣거나 검색해서 우리 상품의 차별점, 약점, 강조할 포인트를 표로 정리하고 싶습니다."),
        ("상세페이지 FAQ 문구", "상품 문의와 고객 걱정 포인트를 넣으면 상세페이지 하단에 넣을 FAQ 문구를 만들고 싶습니다."),
        ("전환형/정보형 문구 분리", "상품 설명을 넣으면 구매를 유도하는 전환형 문구와 정보를 전달하는 정보형 문구를 나눠 작성하고 싶습니다."),
    ],
}


def load_env_value(name: str) -> str:
    """Read a single value from .env without adding another dependency."""
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if not os.path.exists(env_path):
        return ""

    with open(env_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            if key.strip() == name:
                return value.strip().strip('"').strip("'")

    return ""


def load_sample_input() -> str:
    sample_path = os.path.join(os.path.dirname(__file__), "sample_input.txt")
    if not os.path.exists(sample_path):
        return DEFAULT_INPUT

    with open(sample_path, "r", encoding="utf-8") as file:
        return file.read().strip()


def load_sample_report_input() -> str:
    sample_path = os.path.join(os.path.dirname(__file__), "sample_report_input.txt")
    if not os.path.exists(sample_path):
        return DEFAULT_REPORT_INPUT

    with open(sample_path, "r", encoding="utf-8") as file:
        return file.read().strip()


def load_sample_work_input() -> str:
    sample_path = os.path.join(os.path.dirname(__file__), "sample_work_input.txt")
    if not os.path.exists(sample_path):
        return DEFAULT_WORK_INPUT

    with open(sample_path, "r", encoding="utf-8") as file:
        return file.read().strip()


def load_project_document() -> str:
    document_path = os.path.join(
        os.path.dirname(__file__),
        "프로젝트문서_직장인사무업무AI사용법검색.md",
    )
    if not os.path.exists(document_path):
        return "프로젝트 문서를 찾을 수 없습니다."

    with open(document_path, "r", encoding="utf-8") as file:
        return file.read()


def make_result_filename(mode: str) -> str:
    if "검색해서 보고서" in mode:
        prefix = "search_report"
    elif "사무업무" in mode:
        prefix = "office_ai_workflow"
    else:
        prefix = "ai_video_plan"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.txt"


def save_result_file(result: str, mode: str) -> str:
    output_dir = os.path.join(os.path.dirname(__file__), "outputs")
    os.makedirs(output_dir, exist_ok=True)

    filename = make_result_filename(mode)
    output_path = os.path.join(output_dir, filename)
    with open(output_path, "w", encoding="utf-8-sig") as file:
        file.write(result)

    return output_path


def apply_popular_task(task_index: int, selected_mode: str) -> None:
    task = POPULAR_OFFICE_AI_TASKS[task_index]

    if "영상 기획서" in selected_mode:
        st.session_state.input_text = (
            f"{task['title']} 업무를 주제로 직장인 AI 꿀팁 쇼츠 영상을 만들고 싶습니다.\n\n"
            f"{task['text']}"
        )
    elif "검색해서 보고서" in selected_mode:
        st.session_state.report_input_text = (
            f"{task['title']}에 대해 사무직 직장인이 알아야 할 최신 활용 방법을 검색해서 보고서로 정리해주세요.\n\n"
            f"{task['text']}"
        )
    else:
        st.session_state.work_input_text = task["text"]

    st.session_state.selected_popular_task = task["title"]
    st.session_state.selected_popular_task_text = task["text"]


def apply_role_task(role: str, title: str, task_text: str) -> None:
    st.session_state.work_input_text = (
        f"{role} 업무 중 '{title}'을 처리하고 싶습니다.\n\n"
        f"{task_text}\n\n"
        "AI를 잘 모르는 사람도 따라 할 수 있게, 준비할 자료와 실행 순서를 쉽게 알려주세요."
    )
    st.session_state.selected_role_task = f"{role} - {title}"
    st.session_state.use_mode_choice = "쉬운 선택"


def create_prompt(keyword: str) -> str:
    return f"""
당신은 직장인 대상 유튜브 쇼츠/릴스 영상 제작 PD이자 촬영 지시서를 만드는 전문가입니다.

아래 입력 내용을 바탕으로, 사무직 직장인이 AI(Claude, ChatGPT, Gemini 등)로
반복 업무를 빠르게 처리하는 15~20초짜리 AI 꿀팁 영상 제작안 1개를 완성도 있게 만들어주세요.
마지막에는 같은 방향의 예비 주제 2개만 짧게 제안해주세요.

중요:
- 단순 아이디어가 아니라, 촬영자가 그대로 보고 영상을 만들 수 있는 "제작 지시서"로 작성하세요.
- 각 기획안은 반드시 끝까지 완성하세요.
- 문장이 중간에서 끊기면 안 됩니다.

[사용자 입력]
{keyword}

아래 형식을 반드시 지켜주세요.

---
# 바로 촬영 가능한 영상 제작안

1. 영상 제목
-

2. 영상 콘셉트
- 대상 시청자:
- 해결할 문제:
- 영상 톤:
- 시청자가 얻는 결과:

3. 15~20초 장면 구성표
| 시간 | 화면 | 내레이션/대사 | 자막 | 촬영/편집 메모 |
|---|---|---|---|---|
| 0~3초 |  |  |  |  |
| 3~7초 |  |  |  |  |
| 7~13초 |  |  |  |  |
| 13~18초 |  |  |  |  |

4. 촬영용 전체 대본
- 오프닝:
- 본문:
- 마무리:

5. 실제로 AI에게 입력할 프롬프트
```text
여기에 바로 복사해서 쓸 수 있는 프롬프트 작성
```

6. 촬영에 필요한 예시 자료
- 예시 엑셀/문서에 들어갈 컬럼 또는 내용:
- 보여줄 전 화면:
- 보여줄 후 화면:

7. 준비물 체크리스트
- 
- 
- 

8. 편집 체크리스트
- 첫 3초에 문제 상황이 보이는가:
- AI 프롬프트가 화면에 보이는가:
- 전/후 비교가 보이는가:
- 마지막에 따라 해보고 싶게 끝나는가:

9. 예비 주제 2개
- 예비 주제 1:
- 예비 주제 2:

10. 완성 영상 한 줄 설명
-
---

작성 조건:
- 직업군을 너무 좁히지 말고 모든 사무직이 공감할 수 있게 작성
- 제목은 직장인이 바로 클릭하고 싶게 구체적으로 작성
- AI 프롬프트는 실제로 복사해서 쓸 수 있게 작성
- 대본은 짧고 자연스럽게, 바로 촬영 가능한 말투로 작성
- 화면 예시는 "엑셀 화면", "AI 채팅창", "전/후 비교"처럼 실제 촬영 장면으로 작성
- 어려운 전문 용어 없이 초보자도 이해할 수 있게 작성
- 과장된 자동화 표현보다, 실제 업무 시간을 줄이는 실용적인 팁으로 작성
- 결과는 반드시 한국어로 작성
- 메인 제작안 1개는 반드시 촬영 가능한 수준으로 자세히 작성
- 예비 주제 2개는 제목과 핵심 아이디어만 짧게 작성
""".strip()


def create_report_prompt(topic: str) -> str:
    return f"""
당신은 바쁜 사무직 직장인을 위해 필요한 정보를 검색하고 보고서로 정리해주는 AI 직원입니다.

아래 요청에 대해 최신 정보를 검색해서, 바로 업무에 활용할 수 있는 한국어 보고서로 정리해주세요.

[사용자 요청]
{topic}

아래 형식으로 작성해주세요.

---
# 검색 기반 업무 보고서

## 1. 핵심 요약
- 중요한 내용 3~5개를 짧게 정리

## 2. 지금 알아야 할 배경
- 왜 이 정보가 중요한지 설명

## 3. 업무에 바로 쓰는 정리
- 사무직이 실제 업무에서 활용할 수 있는 방식으로 정리

## 4. 보고서/콘텐츠에 넣을 문장
- 그대로 복사해서 쓸 수 있는 문장 3개

## 5. 자료 검증표
아래 표 형식으로 작성

| 자료/출처 | 핵심 내용 | 최신성 | 신뢰도 | 업무 적합도 | 선호도 | 판단 이유 |
|---|---|---:|---:|---:|---:|---|

- 최신성, 신뢰도, 업무 적합도, 선호도는 1~5점으로 평가
- 신뢰도는 공식 기관/기업/언론/전문 보고서 여부를 기준으로 판단
- 업무 적합도는 사무직이 실제로 따라 할 수 있는지 기준으로 판단
- 선호도는 사용자의 요청에 얼마나 잘 맞는지 기준으로 판단

## 6. 최종 추천 우선순위
- 가장 먼저 참고할 자료 1~3순위와 이유

## 7. 추가로 확인하면 좋은 질문
- 다음 조사에 쓸 질문 3개

## 8. 참고 출처
- 검색에서 확인한 주요 출처를 제목과 링크로 정리
---

작성 조건:
- 검색 결과에 근거해서 작성
- 모르는 내용은 단정하지 말고 "추가 확인 필요"라고 표시
- 너무 긴 설명보다 실제 업무에 쓸 수 있는 형태로 정리
- 출처가 있는 내용과 의견/제안을 구분
- 출처가 부족하거나 애매한 내용은 신뢰도 점수를 낮게 주고 이유를 설명
- 선호도 점수가 높은 자료일수록 사용자의 목적에 더 직접적으로 맞아야 함
- 한국어로 자연스럽게 작성
""".strip()


def create_work_prompt(task: str) -> str:
    return f"""
당신은 사무직 직장인의 반복 업무를 AI로 처리하게 도와주는 업무 자동화 코치입니다.

사용자는 아래 사무업무를 AI로 처리하고 싶어합니다.
최신 검색 정보를 참고해서, 이 업무를 AI로 처리할 수 있는지 판단하고
실제로 따라 할 수 있는 처리 방법을 제시해주세요.

[사용자 업무]
{task}

아래 형식을 반드시 지켜주세요.

---
# AI 사무업무 처리 가이드

## 1. 처리 가능 여부
- 가능 / 부분 가능 / 어려움 중 하나로 판단:
- 그렇게 판단한 이유:
- AI로 줄일 수 있는 작업:
- 사람이 직접 확인해야 하는 작업:

## 2. 추천 처리 방법
| 단계 | 사용 도구 | 사용자가 할 일 | AI에게 맡길 일 | 예상 결과물 |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |

## 3. 바로 복사해서 쓰는 AI 프롬프트
```text
여기에 사용자가 바로 복사해서 ChatGPT, Claude, Gemini 등에 넣을 수 있는 프롬프트 작성
```

## 4. 입력 자료 준비 방법
- AI에 넣기 전에 정리해야 할 자료:
- 개인정보나 민감정보를 가리는 방법:
- 파일/표를 붙여넣을 때 주의할 점:

## 5. 결과물 예시
- AI가 어떤 형태로 결과를 내야 하는지 예시 작성
- 표, 체크리스트, 보고서 초안 중 적합한 형식으로 작성

## 6. 결과 검수 체크리스트
- 숫자/금액이 맞는지 확인:
- 누락된 항목이 없는지 확인:
- 원본 자료와 비교해야 할 부분:
- 사람이 최종 판단해야 할 부분:

## 7. 더 정확하게 처리하기 위한 추가 질문
- 사용자가 AI에게 추가로 물어보면 좋은 질문 3개

## 8. 참고한 검색 기준
- 어떤 기준으로 방법을 찾고 판단했는지 설명
- 참고할 만한 키워드나 출처 유형 제안
---

작성 조건:
- 단순 설명이 아니라 실제 업무 처리 순서로 작성
- 사용자가 바로 따라 할 수 있게 구체적으로 작성
- AI가 할 수 없는 부분은 솔직하게 구분
- 민감정보, 개인정보, 회사 기밀은 가려야 한다고 안내
- 한국어로 자연스럽게 작성
""".strip()


def add_user_options_prompt(base_prompt: str, output_format: str, output_style: str) -> str:
    return f"""
{base_prompt}

[사용자 선택 옵션]
- 원하는 결과 형식: {output_format}
- 원하는 결과 스타일: {output_style}

위 선택 옵션을 반드시 반영해서 작성해주세요.
""".strip()


def extract_text(data: dict) -> str:
    candidates = data.get("candidates", [])
    if not candidates:
        raise RuntimeError("AI 응답이 비어 있습니다. 잠시 후 다시 시도해주세요.")

    parts = candidates[0].get("content", {}).get("parts", [])
    result = "\n".join(part.get("text", "") for part in parts).strip()
    if not result:
        raise RuntimeError("AI가 텍스트 결과를 반환하지 않았습니다.")

    return result


def extract_sources(data: dict) -> list[dict[str, str]]:
    candidates = data.get("candidates", [])
    if not candidates:
        return []

    metadata = candidates[0].get("groundingMetadata", {})
    chunks = metadata.get("groundingChunks", [])
    sources = []
    seen = set()

    for chunk in chunks:
        web = chunk.get("web", {})
        uri = web.get("uri", "")
        title = web.get("title", uri)
        if uri and uri not in seen:
            seen.add(uri)
            sources.append({"title": title or uri, "uri": uri})

    return sources


def call_gemini(api_key: str, prompt: str, use_search: bool = False) -> tuple[str, list[dict[str, str]]]:
    model = "gemini-2.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key,
    }
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}],
            }
        ],
        "generationConfig": {
            "temperature": 0.8,
            "maxOutputTokens": 6000,
        },
    }

    if use_search:
        payload["tools"] = [{"google_search": {}}]

    response = requests.post(url, headers=headers, json=payload, timeout=60)
    if not response.ok:
        try:
            message = response.json()["error"]["message"]
        except Exception:
            message = response.text
        raise RuntimeError(message)

    data = response.json()
    return extract_text(data), extract_sources(data)


def generate_plan(api_key: str, keyword: str) -> tuple[str, list[dict[str, str]]]:
    return call_gemini(api_key, create_prompt(keyword), use_search=False)


def generate_report(
    api_key: str,
    topic: str,
    output_format: str = "보고서",
    output_style: str = "실무 실행용",
) -> tuple[str, list[dict[str, str]]]:
    prompt = add_user_options_prompt(create_report_prompt(topic), output_format, output_style)
    return call_gemini(api_key, prompt, use_search=True)


def generate_work_guide(
    api_key: str,
    task: str,
    output_format: str = "체크리스트",
    output_style: str = "실무 실행용",
) -> tuple[str, list[dict[str, str]]]:
    prompt = add_user_options_prompt(create_work_prompt(task), output_format, output_style)
    return call_gemini(api_key, prompt, use_search=True)


def validate_result(result: str, mode: str) -> None:
    if "영상 기획서" in mode:
        required_keywords = [
            "바로 촬영 가능한 영상 제작안",
            "15~20초 장면 구성표",
            "촬영용 전체 대본",
            "실제로 AI에게 입력할 프롬프트",
            "준비물 체크리스트",
            "편집 체크리스트",
        ]
        minimum_length = 1600
    else:
        required_keywords = [
            "핵심 요약" if "검색해서 보고서" in mode else "처리 가능 여부",
            "참고 출처" if "검색해서 보고서" in mode else "추천 처리 방법",
        ]
        minimum_length = 1200

        if "검색해서 보고서" in mode:
            required_keywords.extend(["자료 검증표", "최종 추천 우선순위"])
        else:
            required_keywords.extend(["바로 복사해서 쓰는 AI 프롬프트"])

    missing = [keyword for keyword in required_keywords if keyword not in result]
    if missing or len(result) < minimum_length:
        missing_text = ", ".join(missing) if missing else "결과 길이가 너무 짧음"
        raise RuntimeError(
            f"AI 응답이 완성되지 않았습니다. 다시 실행해주세요. 부족한 항목: {missing_text}"
        )


st.set_page_config(page_title="직장인 사무업무 AI 사용법 검색", page_icon="💼", layout="wide")
st.title("직장인 사무업무 AI 사용법 검색")
st.caption("사무업무에 AI를 어떻게 활용할 수 있는지 검색하고, 정리하고, 실행 방법까지 안내합니다.")

api_key = load_env_value("GOOGLE_API_KEY")

if "last_result" not in st.session_state:
    st.session_state.last_result = ""
if "last_keyword" not in st.session_state:
    st.session_state.last_keyword = ""
if "last_sources" not in st.session_state:
    st.session_state.last_sources = []
if "last_mode" not in st.session_state:
    st.session_state.last_mode = ""
if "last_saved_path" not in st.session_state:
    st.session_state.last_saved_path = ""
if "last_download_name" not in st.session_state:
    st.session_state.last_download_name = "result.txt"
if "input_text" not in st.session_state:
    st.session_state.input_text = load_sample_input()
if "report_input_text" not in st.session_state:
    st.session_state.report_input_text = load_sample_report_input()
if "work_input_text" not in st.session_state:
    st.session_state.work_input_text = load_sample_work_input()
if "selected_popular_task" not in st.session_state:
    st.session_state.selected_popular_task = ""
if "selected_popular_task_text" not in st.session_state:
    st.session_state.selected_popular_task_text = ""
if "selected_role_task" not in st.session_state:
    st.session_state.selected_role_task = ""
if "use_mode_choice" not in st.session_state:
    st.session_state.use_mode_choice = "쉬운 선택"

with st.sidebar:
    st.header("설정")
    if api_key:
        st.success(".env에서 GOOGLE_API_KEY를 불러왔습니다.")
    else:
        st.warning(".env에서 GOOGLE_API_KEY를 찾지 못했습니다.")
        api_key = st.text_input("Google API Key", type="password", placeholder="AIza...")

    st.divider()
    st.markdown("**오늘 MVP 범위**")
    st.markdown("- 직무별 업무 선택\n- AI 업무 처리 방법 생성\n- 결과 다운로드")

    st.divider()
    st.download_button(
        label="업무 처리 예시 파일 다운로드",
        data=load_sample_work_input().encode("utf-8-sig"),
        file_name="sample_work_input.txt",
        mime="text/plain",
    )
    st.download_button(
        label="회의용 프로젝트 문서 다운로드",
        data=load_project_document().encode("utf-8-sig"),
        file_name="project_document_office_ai.md",
        mime="text/markdown",
    )

st.markdown("### 사용 방식")
mode_col1, mode_col2 = st.columns(2)
with mode_col1:
    if st.button("쉬운 선택", type="primary" if st.session_state.use_mode_choice == "쉬운 선택" else "secondary", use_container_width=True):
        st.session_state.use_mode_choice = "쉬운 선택"
with mode_col2:
    if st.button("직접 입력", type="primary" if st.session_state.use_mode_choice == "직접 입력" else "secondary", use_container_width=True):
        st.session_state.use_mode_choice = "직접 입력"

if st.session_state.use_mode_choice == "쉬운 선택":
    st.markdown("### 처음이라면 여기서 시작하세요")
    st.caption("내 직무를 고르고, 자주 하는 업무를 누르면 아래 입력창이 자동으로 채워집니다.")

    role_tabs = st.tabs(list(ROLE_TASKS.keys()))
    for role_tab, (role, tasks) in zip(role_tabs, ROLE_TASKS.items()):
        with role_tab:
            task_cols = st.columns(3)
            for index, (title, task_text) in enumerate(tasks):
                with task_cols[index % 3]:
                    st.button(
                        title,
                        key=f"role_task_{role}_{index}",
                        use_container_width=True,
                        on_click=apply_role_task,
                        args=(role, title, task_text),
                    )

    if st.session_state.selected_role_task:
        st.success(f"선택한 업무: {st.session_state.selected_role_task}")
        st.info("아래 입력창에 내용이 채워졌습니다. 바로 AI 직원 실행하기를 누르면 됩니다.")
else:
    st.markdown("### 직접 입력")
    st.caption("AI 활용에 익숙하다면 원하는 업무를 자유롭게 적어주세요.")

st.subheader("어떤 사무업무를 끝내고 싶나요?")

if st.button("업무 처리 예시 내용으로 채우기"):
    st.session_state.work_input_text = load_sample_work_input()

keyword = st.text_area(
    "처리하고 싶은 업무를 적어주세요",
    key="work_input_text",
    height=190,
    placeholder="예: 회의록을 보고 결정사항과 할 일을 정리하고 싶어요.",
)

st.subheader("AI 직원 실행")

if st.button("AI 직원 실행하기", type="primary"):
    if not api_key.strip():
        st.warning("Google API 키가 필요합니다. .env 파일에 GOOGLE_API_KEY를 넣어주세요.")
    elif not keyword.strip():
        st.warning("업무 상황 또는 키워드를 입력해주세요.")
    else:
        with st.spinner("AI 직원이 작업하는 중입니다..."):
            try:
                result, sources = generate_work_guide(api_key.strip(), keyword.strip())

                mode = "AI로 사무업무 처리하기"
                validate_result(result, mode)

                st.session_state.last_result = result
                st.session_state.last_keyword = keyword.strip()
                st.session_state.last_sources = sources
                st.session_state.last_mode = mode
                st.session_state.last_download_name = make_result_filename(mode)
                st.session_state.last_saved_path = save_result_file(result, mode)
                st.success("생성 완료!")
            except Exception as error:
                if "AI 응답이 완성되지 않았습니다" in str(error):
                    st.error("AI가 결과를 끝까지 완성하지 못했습니다. 같은 내용으로 한 번 더 실행해주세요.")
                else:
                    st.error(
                        "오류가 발생했습니다. API 연결 또는 Gemini 사용 설정을 확인해주세요."
                    )
                st.code(str(error), language="text")

if st.session_state.last_result:
    st.subheader("생성 결과 확인")
    st.info("아래 결과는 화면을 다시 그려도 유지됩니다. 다운로드 버튼을 눌러도 결과가 사라지지 않습니다.")
    if st.session_state.last_saved_path:
        st.success("결과 파일이 PC에 자동 저장되었습니다.")
        st.code(st.session_state.last_saved_path, language="text")

    tab_preview, tab_copy = st.tabs(["보기", "복사용 텍스트"])
    with tab_preview:
        st.markdown(st.session_state.last_result)
        if st.session_state.last_sources:
            st.markdown("### 확인된 참고 출처")
            st.caption("AI가 검색 과정에서 확인한 출처입니다. 본문 안의 자료 검증표와 함께 보세요.")
            for index, source in enumerate(st.session_state.last_sources, start=1):
                st.markdown(f"{index}. [{source['title']}]({source['uri']})")

    with tab_copy:
        st.text_area(
            "생성된 기획서 전체 텍스트",
            value=st.session_state.last_result,
            height=420,
        )

    download_col, save_col = st.columns(2)
    with download_col:
        st.download_button(
            label="결과 다운로드",
            data=st.session_state.last_result.encode("utf-8-sig"),
            file_name=st.session_state.last_download_name,
            mime="text/plain; charset=utf-8",
            key=f"download_{st.session_state.last_download_name}",
            use_container_width=True,
        )
    with save_col:
        if st.button("PC에 파일로 다시 저장", use_container_width=True):
            st.session_state.last_saved_path = save_result_file(
                st.session_state.last_result,
                st.session_state.last_mode,
            )
            st.success("다시 저장했습니다.")
            st.code(st.session_state.last_saved_path, language="text")
