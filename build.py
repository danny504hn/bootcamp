"""Convierte el temario (contenido/*.txt) en JSON con HTML y lo inyecta en la plantilla."""
import html
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).parent
SEC_KEYS = {"titulo", "objetivo", "reto", "hecho", "minima", "pista1", "pista2", "pista3", "guia"}
WEEK_KEYS = {"bloque", "titulo", "resumen", "sabes", "nuevo", "objetivos", "tracker", "opcional"}
LIST_KEYS = {"sabes", "nuevo", "objetivos", "hecho", "guia"}
MD_KEYS = {"reto", "minima", "pista1", "pista2", "pista3"}
KEY_RE = re.compile(r"^([a-z0-9]+):\s?(.*)$")


def inline(text: str) -> str:
    """Escapa HTML y aplica `code` y **negrita** / *cursiva*."""
    codes = []

    def guardar(m):
        codes.append("<code>" + html.escape(m.group(1), quote=False) + "</code>")
        return f"\x00{len(codes) - 1}\x00"

    t = re.sub(r"`([^`]*)`", guardar, text)
    e = html.escape(t, quote=False)
    e = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", e)
    e = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", e)
    e = re.sub(r"\x00(\d+)\x00", lambda m: codes[int(m.group(1))], e)
    return e


def markdown(text: str) -> str:
    lines = text.rstrip("\n").split("\n")
    html_out = []
    i = 0
    para = []

    def flush_para():
        if para:
            html_out.append("<p>" + inline(" ".join(s.strip() for s in para)) + "</p>")
            para.clear()

    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("```"):
            flush_para()
            lang = line.strip()[3:].strip()
            i += 1
            code = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i])
                i += 1
            i += 1  # cierre
            cls = f' class="lang-{lang}"' if lang else ""
            html_out.append(f"<pre><code{cls}>" + html.escape("\n".join(code), quote=False) + "</code></pre>")
            continue
        m_ul = re.match(r"^- (.*)$", line)
        m_ol = re.match(r"^(\d+)\. (.*)$", line)
        if m_ul or m_ol:
            flush_para()
            ordered = bool(m_ol)
            tag = "ol" if ordered else "ul"
            start = int(m_ol.group(1)) if ordered else 1
            attrs = f' start="{start}"' if ordered and start != 1 else ""
            items = []
            while i < len(lines):
                ln = lines[i]
                mu = re.match(r"^- (.*)$", ln)
                mo = re.match(r"^(\d+)\. (.*)$", ln)
                mn = re.match(r"^\s{2,}- (.*)$", ln)
                if (ordered and mo) or (not ordered and mu):
                    items.append([(mo or mu).group(2 if mo else 1), []])
                    i += 1
                elif mn and items:
                    items[-1][1].append(mn.group(1))
                    i += 1
                elif ln.startswith("   ") and ln.strip() and items and not ln.strip().startswith("```"):
                    items[-1][0] += " " + ln.strip()
                    i += 1
                else:
                    break
            lis = []
            for txt, sub in items:
                s = inline(txt)
                if sub:
                    s += "<ul>" + "".join("<li>" + inline(x) + "</li>" for x in sub) + "</ul>"
                lis.append("<li>" + s + "</li>")
            html_out.append(f"<{tag}{attrs}>" + "".join(lis) + f"</{tag}>")
            continue
        if not line.strip():
            flush_para()
            i += 1
            continue
        para.append(line)
        i += 1
    flush_para()
    return "".join(html_out)


def parse_file(path: Path):
    weeks = []
    week = None
    sec = None
    key = None
    buf = []
    in_fence = False

    def target():
        return sec if sec is not None else week

    def commit():
        nonlocal key, buf
        if key is None:
            return
        tgt = target()
        raw = "\n".join(buf).strip("\n")
        if key in LIST_KEYS:
            items = [ln[2:].strip() for ln in raw.split("\n") if ln.startswith("- ")]
            tgt[key] = [inline(x) for x in items]
        elif key in MD_KEYS:
            tgt[key] = markdown(raw)
        elif key in ("bloque",):
            tgt[key] = int(raw.strip())
        elif key == "opcional":
            tgt[key] = raw.strip().lower() in ("si", "sí", "true")
        else:
            tgt[key] = inline(raw.strip())
        key, buf = None, []

    for line in path.read_text(encoding="utf-8").split("\n"):
        if not in_fence and line.startswith("=== SEMANA "):
            commit()
            sec = None
            week = {"n": int(line.split()[2]), "sesiones": {}}
            weeks.append(week)
            continue
        if not in_fence and line.startswith("--- "):
            commit()
            name = line[4:].strip()
            sec = {}
            week["sesiones"][name] = sec
            continue
        if line.strip().startswith("```"):
            in_fence = not in_fence
        if not in_fence:
            m = KEY_RE.match(line)
            allowed = SEC_KEYS if sec is not None else WEEK_KEYS
            if m and m.group(1) in allowed:
                commit()
                key = m.group(1)
                buf = [m.group(2)] if m.group(2) else []
                continue
        if key is not None:
            buf.append(line)
    commit()
    return weeks


def main():
    weeks = []
    for f in sorted((BASE / "contenido").glob("*.txt")):
        weeks.extend(parse_file(f))
    weeks.sort(key=lambda w: w["n"])
    # validación
    problems = []
    for w in weeks:
        for k in ("bloque", "titulo", "resumen", "sabes", "nuevo", "objetivos", "tracker"):
            if k not in w:
                problems.append(f"S{w['n']:02d} falta {k}")
        for s in ("construir", "medir", "aplicar"):
            ses = w["sesiones"].get(s)
            if not ses:
                problems.append(f"S{w['n']:02d} falta sesión {s}")
                continue
            for k in ("titulo", "objetivo", "reto", "hecho", "minima", "pista1", "pista2", "pista3"):
                if not ses.get(k):
                    problems.append(f"S{w['n']:02d}/{s} falta {k}")
        ex = w["sesiones"].get("explica")
        if not ex or not ex.get("reto") or not ex.get("guia"):
            problems.append(f"S{w['n']:02d} explica incompleto")
    if problems:
        print("\n".join(problems))
        sys.exit(1)
    data = json.dumps(weeks, ensure_ascii=False, separators=(",", ":"))
    data = data.replace("</", "<\\/")
    tpl = (BASE / "plantilla.html").read_text(encoding="utf-8")
    out = tpl.replace("/*__TEMARIO__*/[]", data)
    (BASE / "index.html").write_text(out, encoding="utf-8")
    print(f"OK: {len(weeks)} semanas, index.html {len(out)//1024} KB")


if __name__ == "__main__":
    main()
