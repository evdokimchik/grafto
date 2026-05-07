#!/usr/bin/env python3
"""Add answer-first summaries and FAQ schema to generated article pages."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def strip_tags(value: str) -> str:
    value = re.sub(r"<[^>]+>", "", value)
    return html.unescape(value).strip()


def faq_items(title: str, desc: str, lang: str) -> list[tuple[str, str]]:
    clean_title = title.rstrip(" ?")
    if lang == "ru":
        return [
            (
                f"Короткий ответ по теме «{clean_title}»?",
                f"{desc} Используйте этот материал как подготовку к разговору с квалифицированным специалистом.",
            ),
            (
                "Как Grafto помогает с этим решением?",
                "Grafto помогает оценить стадию, подготовить диапазон графтов и стоимости, сравнить пересадку с SMP, сохранить заметки и собрать вопросы к клинике.",
            ),
            (
                "Это медицинская рекомендация?",
                "Нет. Grafto дает образовательную информацию и помогает подготовиться. Итоговый диагноз, план лечения и решение об операции нужно принимать с квалифицированным специалистом.",
            ),
        ]
    return [
        (
            f"What is the short answer about {clean_title}?",
            f"{desc} Use this guide as educational preparation before speaking with a qualified clinician.",
        ),
        (
            "How can Grafto help with this decision?",
            "Grafto helps you assess your stage, estimate graft and cost ranges, compare transplant and SMP options, save notes, and prepare clinic questions.",
        ),
        (
            "Is this medical advice?",
            "No. Grafto provides educational decision support. Final diagnosis, treatment planning, and surgery decisions should be made with a qualified clinician.",
        ),
    ]


def faq_schema(title: str, desc: str, lang: str) -> str:
    data = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": question,
                "acceptedAnswer": {"@type": "Answer", "text": answer},
            }
            for question, answer in faq_items(title, desc, lang)
        ],
    }
    return f'  <script type="application/ld+json">{json.dumps(data, ensure_ascii=False, separators=(",", ":"))}</script>'


def faq_section(title: str, desc: str, lang: str) -> str:
    details = []
    for index, (question, answer) in enumerate(faq_items(title, desc, lang)):
        open_attr = " open" if index == 0 else ""
        details.append(
            f"""        <details{open_attr}>
          <summary>{html.escape(question)}</summary>
          <p>{html.escape(answer)}</p>
        </details>"""
        )
    return f"""      <section class="article-faq" aria-label="FAQ">
        <h2>FAQ</h2>
{chr(10).join(details)}
      </section>
"""


def update_article(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text
    lang_match = re.search(r'<html lang="([^"]+)"', text)
    title_match = re.search(r"<h1>(.*?)</h1>", text, flags=re.S)
    summary_match = re.search(r'<p class="article-summary">(.*?)</p>', text, flags=re.S)
    if not (lang_match and title_match and summary_match):
        return False

    lang = lang_match.group(1)
    title = strip_tags(title_match.group(1))
    desc = strip_tags(summary_match.group(1))
    desc = re.sub(r"^(Quick answer|Короткий ответ):\s*", "", desc).strip()
    plain_items = re.findall(
        r'<section class="article-plain-summary".*?</section>',
        text,
        flags=re.S,
    )
    if plain_items:
        bullets = [strip_tags(item) for item in re.findall(r"<li>(.*?)</li>", plain_items[0], flags=re.S)]
        if bullets:
            desc = " ".join(bullets[:2])
    quick_label = "Короткий ответ" if lang == "ru" else "Quick answer"
    summary_replacement = f'<p class="article-summary"><strong>{html.escape(quick_label)}:</strong> {html.escape(desc)}</p>'
    text = text[: summary_match.start()] + summary_replacement + text[summary_match.end() :]

    text = re.sub(r"style\.css\?v=\d+", "style.css?v=12", text)

    text = re.sub(
        r'\n  <script type="application/ld\+json">\{"@context":"https://schema.org","@type":"FAQPage".*?</script>',
        "",
        text,
        flags=re.S,
    )
    breadcrumb_pattern = re.compile(
        r'(<script type="application/ld\+json">\{"@context":"https://schema.org","@type":"BreadcrumbList".*?</script>)',
        flags=re.S,
    )
    text = breadcrumb_pattern.sub(r"\1\n" + faq_schema(title, desc, lang), text, count=1)

    text = re.sub(
        r'\n?      <section class="article-faq" aria-label="FAQ">.*?      </section>\n(?=      <div class="article-final-cta">)',
        "\n",
        text,
        flags=re.S,
    )
    text = text.replace('      <div class="article-final-cta">', faq_section(title, desc, lang) + '      <div class="article-final-cta">', 1)

    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> None:
    files = sorted((ROOT / "articles").glob("*/*/index.html"))
    changed = sum(1 for path in files if update_article(path))
    index_path = ROOT / "articles" / "index.html"
    if index_path.exists():
        text = index_path.read_text(encoding="utf-8")
        updated = re.sub(r"style\.css\?v=\d+", "style.css?v=12", text)
        if updated != text:
            index_path.write_text(updated, encoding="utf-8")
            changed += 1
    print(f"Updated {changed} article files")


if __name__ == "__main__":
    main()
