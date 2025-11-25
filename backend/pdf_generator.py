from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.enums import TA_CENTER
import markdown2


def md_to_pdf_better(md_input, pdf_path, input_is_text=False):
    """
    Convert markdown (file OR raw text) into a beautifully formatted PDF.

    Parameters:
        md_input: str
            - If input_is_text=False → md_input is a FILE PATH
            - If input_is_text=True  → md_input is RAW markdown text

        pdf_path: str
            Output PDF file path

        input_is_text: bool
            Whether the markdown is provided as raw text
    """

    # 1. Read input markdown
    if input_is_text:
        md_text = md_input  # <-- raw text directly
    else:
        with open(md_input, "r", encoding="utf-8") as f:
            md_text = f.read()

    # 2. Convert Markdown → HTML
    html = markdown2.markdown(md_text)

    # 3. Create PDF document
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()

    # 4. Custom styles
    title_style = ParagraphStyle(
        name="TitleStyle",
        parent=styles["Heading1"],
        alignment=TA_CENTER,
        fontSize=20,
        spaceAfter=20
    )

    heading_style = ParagraphStyle(
        name="HeadingStyle",
        parent=styles["Heading2"],
        fontSize=14,
        spaceBefore=15,
        spaceAfter=10
    )

    normal_style = ParagraphStyle(
        name="NormalStyle",
        parent=styles["BodyText"],
        fontSize=11,
        leading=16
    )

    bullet_style = ParagraphStyle(
        name="BulletStyle",
        parent=styles["BodyText"],
        leftIndent=20
    )

    story = []

    # 5. Split HTML into paragraphs
    html_lines = html.split("\n")

    for line in html_lines:

        if line.strip().startswith("<h1"):
            story.append(Paragraph(line, title_style))
            story.append(Spacer(1, 12))

        elif line.strip().startswith("<h2"):
            story.append(Paragraph(line, heading_style))
            story.append(Spacer(1, 6))

        elif line.strip().startswith("<li"):
            clean = line.replace("<li>", "").replace("</li>", "")
            story.append(Paragraph("• " + clean, bullet_style))

        elif line.strip() == "":
            story.append(Spacer(1, 10))

        else:
            story.append(Paragraph(line, normal_style))

    # Add a page break at the end
    story.append(PageBreak())

    doc.build(story)

    return pdf_path
