import io
import re
from PIL import Image as PILImage
from matplotlib import mathtext
import base64

def _strip_math_delimiters(expr: str) -> str:
    t = expr.strip()
    if (t.startswith('$$') and t.endswith('$$')):
        return t[2:-2]
    if (t.startswith('$') and t.endswith('$')):
        return t[1:-1]
    if (t.startswith('\\(') and t.endswith('\\)')):
        return t[2:-2]
    if (t.startswith('\\[') and t.endswith('\\]')):
        return t[2:-2]
    return t

def render_latex_to_png_bytes(latex_src: str, dpi: int = 200) -> bytes:
    parser = mathtext.MathTextParser("Bitmap")
    inner = _strip_math_delimiters(latex_src)
    text = f"${inner}$"
    rgba, depth = parser.to_rgba(text, dpi=dpi, fontsize=14)
    pil_img = PILImage.fromarray((rgba * 255).astype('uint8'))
    output = io.BytesIO()
    pil_img.save(output, format='PNG')
    return output.getvalue()

def split_text_and_math(content: str):
    pattern = re.compile(r"(\$\$[\s\S]*?\$\$|\\\[[\s\S]*?\\\]|\\\([\s\S]*?\\\)|\$[\s\S]*?\$)")
    parts = pattern.split(content)
    return parts

def html_render_math_to_img(html: str) -> str:
    if not html:
        return html or ""
    pattern = re.compile(r"(\$\$[\s\S]*?\$\$|\\\[[\s\S]*?\\\]|\\\([\s\S]*?\\\)|\$[\s\S]*?\$)")
    def repl(m):
        src = m.group(0)
        try:
            png = render_latex_to_png_bytes(src)
            b64 = base64.b64encode(png).decode('ascii')
            return f'<img alt="math" style="vertical-align: middle;" src="data:image/png;base64,{b64}" />'
        except Exception:
            return src
    return pattern.sub(repl, html)

