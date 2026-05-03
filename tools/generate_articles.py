from __future__ import annotations

import html
import re
import shutil
import textwrap
import unicodedata
import xml.etree.ElementTree as ET
from datetime import date
from dataclasses import dataclass
from pathlib import Path

from docx import Document


ROOT = Path(__file__).resolve().parents[1]
DOCS = [
    Path.home() / "Desktop" / "Grafto_Articles_10_Bilingual.docx",
    Path.home() / "Desktop" / "Grafto_Clusters2to5_27_Articles.docx",
]
SITE_URL = "https://start.grafto.hair"
APP_URL = "https://apps.apple.com/app/grafto-hair-transplant-smp/id6759666757"
STYLE_VERSION = "7"


CLUSTERS = {
    "cost": {
        "en": "Cost",
        "ru": "Стоимость",
        "cta_en": "Get your graft and cost estimate in Grafto.",
        "cta_ru": "Получите оценку графтов и стоимости в Grafto.",
    },
    "grafts": {
        "en": "Grafts",
        "ru": "Графты",
        "cta_en": "Estimate your graft range before speaking to a clinic.",
        "cta_ru": "Оцените диапазон графтов до разговора с клиникой.",
    },
    "norwood": {
        "en": "Norwood Scale",
        "ru": "Шкала Норвуда",
        "cta_en": "Check your Norwood stage in the app.",
        "cta_ru": "Проверьте стадию по Норвуду в приложении Grafto.",
    },
    "clinic": {
        "en": "Clinic Choice",
        "ru": "Выбор клиники",
        "cta_en": "Download the clinic checklist in Grafto.",
        "cta_ru": "Скачайте чек-лист клиники в Grafto.",
    },
    "smp": {
        "en": "SMP",
        "ru": "SMP",
        "cta_en": "Compare SMP and transplant options in Grafto.",
        "cta_ru": "Сравните SMP и пересадку волос в Grafto.",
    },
}


@dataclass
class Block:
    text: str
    style: str


@dataclass
class Article:
    number: int
    cluster: str
    slug: str
    en_title: str
    ru_title: str
    en_blocks: list[Block]
    ru_blocks: list[Block]


def clean(text: str) -> str:
    return " ".join(text.split())


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def classify_cluster(number: int, source: Path) -> str:
    if source.name.startswith("Grafto_Articles_10"):
        return "cost"
    if 1 <= number <= 7:
        return "grafts"
    if 8 <= number <= 12:
        return "norwood"
    if 13 <= number <= 17:
        return "clinic"
    return "smp"


def parse_doc(path: Path) -> list[Article]:
    doc = Document(path)
    raw = [(i, clean(p.text), p.style.name if p.style else "") for i, p in enumerate(doc.paragraphs)]
    nonempty = [(i, text, style) for i, text, style in raw if text]
    article_starts: list[tuple[int, int, str]] = []
    article_re = re.compile(r"^(\d+)\.\s+(.+)$")

    for pos, (idx, text, _style) in enumerate(nonempty):
        m = article_re.match(text)
        if not m:
            continue
        nxt = nonempty[pos + 1][1] if pos + 1 < len(nonempty) else ""
        if nxt == "[ ENGLISH ]":
            article_starts.append((idx, int(m.group(1)), m.group(2)))

    articles: list[Article] = []
    for start_pos, (start_idx, number, en_title) in enumerate(article_starts):
        end_idx = article_starts[start_pos + 1][0] if start_pos + 1 < len(article_starts) else len(raw)
        blocks = [(text, style) for idx, text, style in raw[start_idx + 1 : end_idx] if text]
        try:
            en_marker = next(i for i, (text, _style) in enumerate(blocks) if text == "[ ENGLISH ]")
            ru_marker = next(i for i, (text, _style) in enumerate(blocks) if text == "[ РУССКИЙ ]")
        except StopIteration as exc:
            raise RuntimeError(f"Could not parse language markers for {en_title} in {path}") from exc

        en_blocks = [Block(text, style) for text, style in blocks[en_marker + 1 : ru_marker]]
        ru_all = [Block(text, style) for text, style in blocks[ru_marker + 1 :]]
        ru_title = ru_all[0].text if ru_all else en_title
        ru_blocks = ru_all[1:] if ru_all else []
        cluster = classify_cluster(number, path)
        articles.append(
            Article(
                number=number,
                cluster=cluster,
                slug=slugify(en_title),
                en_title=en_title,
                ru_title=ru_title,
                en_blocks=en_blocks,
                ru_blocks=ru_blocks,
            )
        )
    return articles


def linkify(text: str) -> str:
    escaped = html.escape(text)
    return re.sub(
        r"(https?://[^\s<]+)",
        lambda m: f'<a href="{m.group(1)}" target="_blank" rel="noopener noreferrer">{m.group(1)}</a>',
        escaped,
    )


def looks_like_heading(text: str, style: str) -> bool:
    if style.startswith("Heading"):
        return True
    if text.startswith("[") and "]" in text:
        return False
    if text.startswith(("http://", "https://")):
        return False
    if len(text) > 82:
        return False
    if text.endswith((".", ":", ";", "?", "!")):
        return False
    return True


def render_blocks(blocks: list[Block]) -> str:
    out: list[str] = []
    in_list = False
    for block in blocks:
        text = block.text
        if block.style == "List Bullet":
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"  <li>{linkify(text)}</li>")
            continue
        if in_list:
            out.append("</ul>")
            in_list = False
        if looks_like_heading(text, block.style):
            out.append(f"<h2>{html.escape(text)}</h2>")
        else:
            out.append(f"<p>{linkify(text)}</p>")
    if in_list:
        out.append("</ul>")
    return "\n".join(out)


def excerpt(blocks: list[Block]) -> str:
    for block in blocks:
        if block.style != "List Bullet" and not looks_like_heading(block.text, block.style):
            if len(block.text) <= 155:
                return block.text
            return block.text[:155].rsplit(" ", 1)[0].rstrip(".,;:") + "..."
    return ""


def page_template(article: Article, lang: str) -> str:
    title = article.en_title if lang == "en" else article.ru_title
    other_title = article.ru_title if lang == "en" else article.en_title
    blocks = article.en_blocks if lang == "en" else article.ru_blocks
    cluster = CLUSTERS[article.cluster]
    cluster_label = cluster[lang]
    cta = cluster[f"cta_{lang}"]
    other_lang = "ru" if lang == "en" else "en"
    desc = excerpt(blocks)
    canonical = f"{SITE_URL}/articles/{lang}/{article.slug}/"
    alternate = f"{SITE_URL}/articles/{other_lang}/{article.slug}/"
    back_label = "All guides" if lang == "en" else "Все материалы"
    app_label = "Open Grafto App" if lang == "en" else "Открыть Grafto"
    cluster_intro = "Guide cluster" if lang == "en" else "Кластер материалов"
    disclaimer = (
        "Educational content only. Final planning should be discussed with a qualified clinician."
        if lang == "en"
        else "Материал носит образовательный характер. Окончательный план нужно обсуждать с квалифицированным специалистом."
    )
    language_label = "Русская версия" if lang == "en" else "English version"

    return f"""<!DOCTYPE html>
<html lang="{lang}" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(title)} | Grafto</title>
  <meta name="description" content="{html.escape(desc)}">
  <link rel="canonical" href="{canonical}">
  <link rel="alternate" hreflang="{lang}" href="{canonical}">
  <link rel="alternate" hreflang="{other_lang}" href="{alternate}">
  <link rel="alternate" hreflang="x-default" href="{SITE_URL}/articles/en/{article.slug}/">
  <meta property="og:type" content="article">
  <meta property="og:title" content="{html.escape(title)}">
  <meta property="og:description" content="{html.escape(desc)}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{SITE_URL}/hero.png">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="stylesheet" href="../../../base.css">
  <link rel="stylesheet" href="../../../style.css?v={STYLE_VERSION}">
  <link rel="icon" href="../../../logo.jpg" type="image/jpeg">
</head>
<body class="article-page">
  <header class="article-topbar">
    <a href="../../../" class="article-logo" aria-label="Grafto home">
      <img src="../../../logo.jpg" alt="Grafto" width="32" height="32">
      <span>Grafto</span>
    </a>
    <nav class="article-topbar__nav" aria-label="Article navigation">
      <a href="../../">{back_label}</a>
      <a href="../../{other_lang}/{article.slug}/">{language_label}</a>
    </nav>
  </header>

  <main class="article-shell">
    <article class="article-content">
      <p class="article-eyebrow">{cluster_intro}: {html.escape(cluster_label)}</p>
      <h1>{html.escape(title)}</h1>
      <p class="article-summary">{html.escape(desc)}</p>
      <div class="article-disclaimer">{html.escape(disclaimer)}</div>
      {render_blocks(blocks)}
      <div class="article-final-cta">
        <p>{html.escape(cta)}</p>
        <a href="{APP_URL}" target="_blank" rel="noopener noreferrer" class="btn btn--primary">{app_label}</a>
      </div>
    </article>
  </main>
</body>
</html>
"""


def index_template(articles: list[Article]) -> str:
    grouped = {key: [] for key in CLUSTERS}
    for article in articles:
        grouped[article.cluster].append(article)

    sections: list[str] = []
    for key, cluster in CLUSTERS.items():
        cards = []
        for article in grouped[key]:
            cards.append(
                f"""<div class="article-index-card">
          <span class="article-index-card__cluster">{html.escape(cluster["en"])}</span>
          <a href="./en/{article.slug}/"><strong>{html.escape(article.en_title)}</strong></a>
          <a href="./ru/{article.slug}/">{html.escape(article.ru_title)}</a>
        </div>"""
            )
        sections.append(
            f"""<section class="article-index-section" id="{key}">
      <div class="section__header">
        <h2 class="section__title">{html.escape(cluster["en"])}</h2>
        <p class="section__subtitle">{html.escape(cluster["cta_en"])}</p>
      </div>
      <div class="article-index-grid">
        {"".join(cards)}
      </div>
    </section>"""
        )

    return f"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Hair Transplant Decision Guides | Grafto</title>
  <meta name="description" content="SEO guides on hair transplant cost, graft counts, Norwood stages, clinic choice, and SMP from Grafto.">
  <link rel="canonical" href="{SITE_URL}/articles/">
  <meta property="og:type" content="website">
  <meta property="og:title" content="Hair Transplant Decision Guides | Grafto">
  <meta property="og:description" content="Guides organized by real patient decisions: cost, grafts, Norwood scale, clinic choice, and SMP.">
  <meta property="og:url" content="{SITE_URL}/articles/">
  <meta property="og:image" content="{SITE_URL}/hero.png">
  <link rel="stylesheet" href="../base.css">
  <link rel="stylesheet" href="../style.css?v={STYLE_VERSION}">
  <link rel="icon" href="../logo.jpg" type="image/jpeg">
</head>
<body class="article-page article-index-page">
  <header class="article-topbar">
    <a href="../" class="article-logo" aria-label="Grafto home">
      <img src="../logo.jpg" alt="Grafto" width="32" height="32">
      <span>Grafto</span>
    </a>
    <nav class="article-topbar__nav" aria-label="Article navigation">
      <a href="../">Home</a>
      <a href="{APP_URL}" target="_blank" rel="noopener noreferrer">App Store</a>
    </nav>
  </header>

  <main class="article-index-shell">
    <section class="article-index-hero">
      <p class="article-eyebrow">Decision guides</p>
      <h1>Hair transplant and SMP guides organized by real decisions</h1>
      <p>Dedicated pages for cost, graft ranges, Norwood stage, clinic choice, and SMP topics. Each guide is built to help users make better decisions before booking a consultation.</p>
    </section>
    {"".join(sections)}
  </main>
</body>
</html>
"""


def update_sitemap(articles: list[Article]) -> None:
    sitemap_path = ROOT / "sitemap.xml"
    ET.register_namespace("", "http://www.sitemaps.org/schemas/sitemap/0.9")
    tree = ET.parse(sitemap_path)
    root = tree.getroot()
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = [f"{SITE_URL}/articles/"]
    for article in articles:
        urls.append(f"{SITE_URL}/articles/en/{article.slug}/")
        urls.append(f"{SITE_URL}/articles/ru/{article.slug}/")
    url_set = set(urls)
    for node in list(root.findall("sm:url", ns)):
        loc = node.find("sm:loc", ns)
        if loc is not None and loc.text in url_set:
            root.remove(node)
    existing = {loc.text for loc in root.findall("sm:url/sm:loc", ns)}
    today = date.today().isoformat()
    for url in urls:
        if url in existing:
            continue
        node = ET.SubElement(root, "{http://www.sitemaps.org/schemas/sitemap/0.9}url")
        loc = ET.SubElement(node, "{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
        loc.text = url
        lastmod = ET.SubElement(node, "{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod")
        lastmod.text = today
        changefreq = ET.SubElement(node, "{http://www.sitemaps.org/schemas/sitemap/0.9}changefreq")
        changefreq.text = "monthly"
        priority = ET.SubElement(node, "{http://www.sitemaps.org/schemas/sitemap/0.9}priority")
        priority.text = "0.7" if url.endswith("/articles/") else "0.6"
    ET.indent(tree, space="  ")
    tree.write(sitemap_path, encoding="utf-8", xml_declaration=True)


def main() -> None:
    articles: list[Article] = []
    for doc in DOCS:
        articles.extend(parse_doc(doc))

    out_dir = ROOT / "articles"
    if out_dir.exists():
        shutil.rmtree(out_dir)
    (out_dir / "en").mkdir(parents=True)
    (out_dir / "ru").mkdir(parents=True)

    (out_dir / "index.html").write_text(index_template(articles), encoding="utf-8")
    for article in articles:
        for lang in ("en", "ru"):
            target = out_dir / lang / article.slug
            target.mkdir(parents=True)
            target.joinpath("index.html").write_text(page_template(article, lang), encoding="utf-8")

    update_sitemap(articles)
    print(f"Generated {len(articles)} bilingual articles ({len(articles) * 2} pages).")
    for key in CLUSTERS:
        print(key, sum(1 for a in articles if a.cluster == key))


if __name__ == "__main__":
    main()
