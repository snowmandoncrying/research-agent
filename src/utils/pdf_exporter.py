"""
PDF 변환 유틸리티
Markdown 리포트를 PDF로 변환합니다.
"""

import os
from datetime import datetime
from io import BytesIO
import markdown
from xhtml2pdf import pisa


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
            font-family: "Malgun Gothic", "맑은 고딕", "Apple SD Gothic Neo", sans-serif;
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
            font-family: "Consolas", "Monaco", monospace;
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


def html_to_pdf(html_content: str, output_path: str) -> bool:
    """
    HTML을 PDF로 변환합니다.

    Args:
        html_content: HTML 문자열
        output_path: PDF 저장 경로

    Returns:
        성공 여부 (True/False)
    """

    try:
        with open(output_path, "wb") as pdf_file:
            # HTML을 PDF로 변환
            pisa_status = pisa.CreatePDF(
                html_content,
                dest=pdf_file,
                encoding='utf-8'
            )

            return not pisa_status.err

    except Exception as e:
        print(f"  ⚠️ PDF 변환 오류: {e}")
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
