"""
PDF 변환 유틸리티
Markdown 리포트를 PDF로 변환합니다.
"""

import os
from datetime import datetime
import markdown
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image
from reportlab.platypus import Table, TableStyle, ListFlowable, ListItem
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from bs4 import BeautifulSoup


def markdown_to_html(markdown_text: str, title: str) -> str:
    """
    Markdown 텍스트를 HTML로 변환합니다.

    Args:
        markdown_text: Markdown 형식의 텍스트
        title: 문서 제목

    Returns:
        HTML 문자열
    """

    # Markdown을 HTML로 변환
    md = markdown.Markdown(extensions=[
        'extra',        # 테이블, 각주 등 확장 기능
        'nl2br',        # 줄바꿈을 <br>로 변환
        'sane_lists',   # 리스트 처리 개선
    ])

    body_html = md.convert(markdown_text)

    # 완전한 HTML 문서 생성 (CSS 스타일 포함)
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        @page {{
            size: A4;
            margin: 2cm;
        }}

        body {{
            font-family: Malgun Gothic, sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #333;
        }}

        h1 {{
            font-size: 24pt;
            font-weight: bold;
            color: #1a1a1a;
            margin-top: 0;
            margin-bottom: 0.5cm;
            padding-bottom: 0.3cm;
            border-bottom: 2px solid #333;
        }}

        h2 {{
            font-size: 18pt;
            font-weight: bold;
            color: #2c2c2c;
            margin-top: 0.8cm;
            margin-bottom: 0.4cm;
            page-break-after: avoid;
        }}

        h3 {{
            font-size: 14pt;
            font-weight: bold;
            color: #444;
            margin-top: 0.6cm;
            margin-bottom: 0.3cm;
            page-break-after: avoid;
        }}

        p {{
            margin: 0.3cm 0;
            text-align: justify;
        }}

        strong, b {{
            font-weight: bold;
            color: #000;
        }}

        em, i {{
            font-style: italic;
        }}

        ul, ol {{
            margin: 0.3cm 0;
            padding-left: 1.5cm;
        }}

        li {{
            margin: 0.2cm 0;
        }}

        a {{
            color: #0066cc;
            text-decoration: none;
        }}

        hr {{
            border: none;
            border-top: 1px solid #ccc;
            margin: 0.5cm 0;
        }}

        code {{
            background-color: #f5f5f5;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: Consolas, monospace;
            font-size: 10pt;
        }}

        pre {{
            background-color: #f5f5f5;
            padding: 0.3cm;
            border-radius: 5px;
            overflow-x: auto;
            margin: 0.3cm 0;
        }}

        pre code {{
            background-color: transparent;
            padding: 0;
        }}

        blockquote {{
            margin: 0.3cm 0;
            padding-left: 0.5cm;
            border-left: 3px solid #ccc;
            color: #666;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 0.3cm 0;
        }}

        th, td {{
            border: 1px solid #ddd;
            padding: 0.2cm;
            text-align: left;
        }}

        th {{
            background-color: #f5f5f5;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    {body_html}
</body>
</html>
    """

    return html


def _register_korean_font():
    """
    한글 폰트를 등록합니다. (Windows 환경)
    """
    try:
        # Windows 기본 한글 폰트 등록
        font_path = "C:/Windows/Fonts/malgun.ttf"  # 맑은 고딕
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont('MalgunGothic', font_path))
            return 'MalgunGothic'
    except:
        pass

    # 폰트 등록 실패시 기본 폰트 사용
    return 'Helvetica'


def _html_to_flowables(html_content: str, styles):
    """
    HTML을 ReportLab Flowable 객체로 변환합니다.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    flowables = []

    # body 태그 내용만 파싱
    body = soup.find('body')
    if not body:
        body = soup

    for element in body.children:
        if element.name is None:  # 텍스트 노드
            continue

        if element.name == 'h1':
            para = Paragraph(element.get_text(), styles['Heading1'])
            flowables.append(para)
            flowables.append(Spacer(1, 0.3*cm))

        elif element.name == 'h2':
            para = Paragraph(element.get_text(), styles['Heading2'])
            flowables.append(para)
            flowables.append(Spacer(1, 0.2*cm))

        elif element.name == 'h3':
            para = Paragraph(element.get_text(), styles['Heading3'])
            flowables.append(para)
            flowables.append(Spacer(1, 0.2*cm))

        elif element.name == 'p':
            text = element.get_text()
            if text.strip():
                para = Paragraph(text, styles['BodyText'])
                flowables.append(para)
                flowables.append(Spacer(1, 0.2*cm))

        elif element.name in ['ul', 'ol']:
            items = []
            for li in element.find_all('li', recursive=False):
                items.append(ListItem(Paragraph(li.get_text(), styles['BodyText'])))
            if items:
                list_flow = ListFlowable(items, bulletType='bullet' if element.name == 'ul' else '1')
                flowables.append(list_flow)
                flowables.append(Spacer(1, 0.2*cm))

        elif element.name == 'img':
            # 이미지 처리
            img_src = element.get('src')
            if img_src:
                # file:// 프로토콜 제거
                if img_src.startswith('file:///'):
                    img_src = img_src[8:]  # file:/// 제거
                elif img_src.startswith('file://'):
                    img_src = img_src[7:]  # file:// 제거

                # 슬래시를 백슬래시로 변환 (Windows 경로 정규화)
                img_src = img_src.replace("/", "\\")

                print(f"  🔍 이미지 경로 확인: {img_src}")
                print(f"  🔍 파일 존재 여부: {os.path.exists(img_src)}")

                if os.path.exists(img_src):
                    try:
                        # 이미지를 페이지 너비에 맞게 조정 (최대 15cm)
                        img = Image(img_src, width=15*cm, height=None, kind='proportional')
                        flowables.append(img)
                        flowables.append(Spacer(1, 0.3*cm))
                        print(f"  ✅ PDF에 차트 삽입 성공: {img_src}")
                    except Exception as e:
                        print(f"  ⚠️ 이미지 삽입 실패 ({img_src}): {e}")
                        import traceback
                        traceback.print_exc()
                else:
                    print(f"  ❌ 이미지 파일을 찾을 수 없음: {img_src}")
                    # 절대경로 시도
                    abs_img_src = os.path.abspath(img_src)
                    print(f"  🔍 절대경로 시도: {abs_img_src}")
                    if os.path.exists(abs_img_src):
                        try:
                            img = Image(abs_img_src, width=15*cm, height=None, kind='proportional')
                            flowables.append(img)
                            flowables.append(Spacer(1, 0.3*cm))
                            print(f"  ✅ PDF에 차트 삽입 성공 (절대경로): {abs_img_src}")
                        except Exception as e:
                            print(f"  ⚠️ 이미지 삽입 실패 ({abs_img_src}): {e}")

    return flowables


def html_to_pdf(html_content: str, output_path: str) -> bool:
    """
    HTML을 PDF로 변환합니다. (ReportLab 사용)

    Args:
        html_content: HTML 문자열
        output_path: PDF 저장 경로

    Returns:
        성공 여부 (True/False)
    """

    try:
        # PDF 문서 생성
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        # 한글 폰트 등록
        korean_font = _register_korean_font()

        # 스타일 정의
        styles = getSampleStyleSheet()

        # 한글 폰트 적용
        styles['Normal'].fontName = korean_font
        styles['BodyText'].fontName = korean_font
        styles['Heading1'].fontName = korean_font
        styles['Heading2'].fontName = korean_font
        styles['Heading3'].fontName = korean_font

        # 스타일 커스터마이징
        styles['Heading1'].fontSize = 24
        styles['Heading1'].spaceAfter = 0.5*cm
        styles['Heading1'].textColor = colors.HexColor('#1a1a1a')

        styles['Heading2'].fontSize = 18
        styles['Heading2'].spaceAfter = 0.4*cm
        styles['Heading2'].textColor = colors.HexColor('#2c2c2c')

        styles['Heading3'].fontSize = 14
        styles['Heading3'].spaceAfter = 0.3*cm
        styles['Heading3'].textColor = colors.HexColor('#444444')

        styles['BodyText'].fontSize = 11
        styles['BodyText'].alignment = TA_JUSTIFY
        styles['BodyText'].textColor = colors.HexColor('#333333')

        # HTML을 Flowable로 변환
        flowables = _html_to_flowables(html_content, styles)

        # PDF 생성
        doc.build(flowables)
        return True

    except Exception as e:
        print(f"  ⚠️ PDF 변환 오류: {e}")
        import traceback
        traceback.print_exc()
        return False


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
        # Markdown을 HTML로 변환
        html_content = markdown_to_html(markdown_content, topic)

        # HTML을 PDF로 변환
        success = html_to_pdf(html_content, pdf_path)

        if success:
            print(f"  ✅ PDF 생성 성공: {pdf_path}")
        else:
            print(f"  ⚠️ PDF 생성 실패")

    except Exception as e:
        print(f"  ⚠️ PDF 생성 실패: {e}")
        import traceback
        traceback.print_exc()

    return pdf_path


# 사용 예시:
# markdown = "# 제목\n\n## 섹션1\n본문 내용..."
# path = save_markdown_as_pdf(markdown, "AI 기술 동향")
# print(f"PDF 저장됨: {path}")
