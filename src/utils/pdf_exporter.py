"""
PDF 변환 유틸리티
Markdown 리포트를 PDF로 변환합니다.
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_CENTER


def setup_korean_font():
    """
    한글 폰트를 설정합니다.

    TODO: 시스템에 설치된 한글 폰트를 찾아서 등록해야 합니다.
    Windows: C:/Windows/Fonts/malgun.ttf (맑은 고딕)
    macOS: /Library/Fonts/AppleGothic.ttf
    Linux: /usr/share/fonts/truetype/nanum/NanumGothic.ttf

    폰트가 없으면 reportlab의 기본 폰트 사용 (한글 깨짐 가능)
    """
    try:
        # Windows 맑은 고딕 시도
        font_path = "C:/Windows/Fonts/malgun.ttf"
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont('Korean', font_path))
            return 'Korean'
    except Exception as e:
        print(f"⚠️ 한글 폰트 등록 실패: {e}")

    # 기본 폰트 사용
    return 'Helvetica'


def markdown_to_pdf_simple(markdown_text: str, output_path: str, title: str):
    """
    Markdown 텍스트를 간단하게 PDF로 변환합니다.

    Args:
        markdown_text: Markdown 형식의 텍스트
        output_path: PDF 저장 경로
        title: 문서 제목
    """

    # PDF 문서 생성
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )

    # 스타일 설정
    styles = getSampleStyleSheet()
    font_name = setup_korean_font()

    # 커스텀 스타일
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=font_name,
        fontSize=24,
        textColor='#333333',
        spaceAfter=30,
        alignment=TA_CENTER,
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontName=font_name,
        fontSize=16,
        textColor='#444444',
        spaceAfter=12,
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontName=font_name,
        fontSize=11,
        leading=16,
        spaceAfter=12,
    )

    # Story (문서 내용)
    story = []

    # 제목 추가
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 0.2 * inch))

    # Markdown 파싱 (간단한 버전)
    # TODO: 더 정교한 Markdown 파싱 라이브러리 사용 가능 (markdown2, mistune 등)
    lines = markdown_text.split('\n')

    for line in lines:
        line = line.strip()

        if not line:
            story.append(Spacer(1, 0.1 * inch))
            continue

        # 제목 처리
        if line.startswith('# '):
            text = line[2:].strip()
            story.append(Paragraph(text, title_style))
        elif line.startswith('## '):
            text = line[3:].strip()
            story.append(Paragraph(text, heading_style))
        elif line.startswith('### '):
            text = line[4:].strip()
            story.append(Paragraph(text, heading_style))
        # 굵은 글씨
        elif line.startswith('**') and line.endswith('**'):
            text = line[2:-2]
            story.append(Paragraph(f"<b>{text}</b>", body_style))
        # 구분선
        elif line.startswith('---'):
            story.append(Spacer(1, 0.2 * inch))
        # 일반 텍스트
        else:
            # HTML 특수문자 이스케이프
            text = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            story.append(Paragraph(text, body_style))

    # PDF 빌드
    doc.build(story)


def save_markdown_as_pdf(markdown_content: str, topic: str) -> str:
    """
    Markdown 리포트를 PDF로 저장합니다.

    Args:
        markdown_content: Markdown 형식의 리포트 내용
        topic: 리포트 주제 (파일명으로 사용)

    Returns:
        저장된 PDF 파일 경로
    """

    # 디렉토리 생성
    os.makedirs("outputs/pdfs", exist_ok=True)

    # 파일명 생성
    safe_filename = "".join(c if c.isalnum() or c in " _-" else "_" for c in topic)
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_path = f"outputs/pdfs/{safe_filename}_{timestamp_str}.pdf"

    try:
        # PDF 생성
        markdown_to_pdf_simple(markdown_content, pdf_path, topic)
        print(f"  ✅ PDF 생성 성공: {pdf_path}")

    except Exception as e:
        print(f"  ⚠️ PDF 생성 실패: {e}")
        # 실패 시 빈 파일 생성
        with open(pdf_path, "w") as f:
            f.write("")

    return pdf_path


# 사용 예시:
# markdown = "# 제목\n\n## 섹션1\n본문 내용..."
# path = save_markdown_as_pdf(markdown, "AI 기술 동향")
# print(f"PDF 저장됨: {path}")
