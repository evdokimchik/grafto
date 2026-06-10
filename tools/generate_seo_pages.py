from __future__ import annotations

import html
import json
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE_URL = "https://start.grafto.hair"
APP_URL = "https://apps.apple.com/app/grafto-hair-transplant-smp/id6759666757"
STYLE_VERSION = "13"
LASTMOD = "2026-06-10"


@dataclass
class ArticleCard:
    slug: str
    title_en: str
    title_ru: str
    excerpt_en: str
    excerpt_ru: str


HUBS = {
    "cost": {
        "path": "cost",
        "label_en": "Cost",
        "label_ru": "Стоимость",
        "title_en": "Hair Transplant Cost Guides",
        "title_ru": "Гайды по стоимости пересадки волос",
        "description_en": "Country, graft-count, and SMP cost guides for people estimating a realistic hair restoration budget before a clinic quote.",
        "description_ru": "Гайды по странам, количеству графтов и стоимости SMP для тех, кто хочет понять реалистичный бюджет до предложения клиники.",
        "quick_en": "Hair transplant cost depends on country, graft count, surgeon involvement, method, aftercare, and what is included in the quote. Use this cluster to compare ranges before you pay a deposit.",
        "quick_ru": "Стоимость пересадки зависит от страны, количества графтов, участия хирурга, метода, сопровождения и того, что входит в цену. Этот раздел помогает сравнить диапазоны до предоплаты.",
        "cta_en": "Get your graft and cost estimate in Grafto.",
        "cta_ru": "Получите оценку графтов и стоимости в Grafto.",
    },
    "grafts": {
        "path": "grafts",
        "label_en": "Grafts",
        "label_ru": "Графты",
        "title_en": "Hair Transplant Graft Guides",
        "title_ru": "Гайды по графтам при пересадке волос",
        "description_en": "Guides that explain graft ranges, donor-area limits, density, temples, crown planning, and overharvesting risks.",
        "description_ru": "Материалы о диапазонах графтов, ограничениях донорской зоны, плотности, висках, макушке и риске чрезмерного изъятия.",
        "quick_en": "Graft numbers are planning ranges, not a shopping target. A safer plan balances coverage goals with donor-area preservation and long-term hair-loss progression.",
        "quick_ru": "Количество графтов — это ориентир для планирования, а не цель любой ценой. Безопасный план учитывает покрытие, сохранение донорской зоны и возможное развитие выпадения.",
        "cta_en": "Estimate your graft range before speaking to a clinic.",
        "cta_ru": "Оцените диапазон графтов до разговора с клиникой.",
    },
    "norwood": {
        "path": "norwood-scale",
        "label_en": "Norwood Scale",
        "label_ru": "Шкала Норвуда",
        "title_en": "Norwood Scale Guides",
        "title_ru": "Гайды по шкале Норвуда",
        "description_en": "Norwood-stage guides for understanding hair loss pattern, likely planning questions, graft ranges, and donor limitations.",
        "description_ru": "Материалы по стадиям Норвуда: рисунок выпадения, вопросы для планирования, диапазоны графтов и ограничения донорской зоны.",
        "quick_en": "The Norwood scale helps describe visible male-pattern hair loss, but it does not decide candidacy by itself. Age, donor area, hair caliber, stability, and expectations matter too.",
        "quick_ru": "Шкала Норвуда помогает описать видимую стадию мужского выпадения волос, но сама по себе не решает, подходит ли пересадка. Важны возраст, донорская зона, толщина волос, стабильность выпадения и ожидания.",
        "cta_en": "Check your Norwood stage in the app.",
        "cta_ru": "Проверьте стадию по Норвуду в приложении Grafto.",
    },
    "clinic": {
        "path": "clinic-choice",
        "label_en": "Clinic Choice",
        "label_ru": "Выбор клиники",
        "title_en": "Hair Transplant Clinic Choice Guides",
        "title_ru": "Гайды по выбору клиники пересадки волос",
        "description_en": "Guides for choosing a clinic, asking consultation questions, reading before/after photos, and spotting red flags before booking.",
        "description_ru": "Гайды о выборе клиники, вопросах на консультации, оценке фото до/после и тревожных сигналах до записи.",
        "quick_en": "A clinic should be judged by surgeon involvement, realistic planning, verified results, clear pricing, follow-up, and how it answers difficult questions.",
        "quick_ru": "Клинику стоит оценивать по участию хирурга, реалистичному плану, подтверждённым результатам, прозрачной цене, сопровождению и тому, как она отвечает на неудобные вопросы.",
        "cta_en": "Download the clinic checklist in Grafto.",
        "cta_ru": "Скачайте чек-лист клиники в Grafto.",
    },
    "smp": {
        "path": "smp",
        "label_en": "SMP",
        "label_ru": "SMP",
        "title_en": "SMP and Scalp Micropigmentation Guides",
        "title_ru": "Гайды по SMP и скальповой микропигментации",
        "description_en": "Guides comparing SMP with hair transplant, SMP costs, healing, diffuse thinning, scars, and failed transplant cases.",
        "description_ru": "Материалы о сравнении SMP и пересадки, стоимости, заживлении, диффузном поредении, рубцах и неудачных пересадках.",
        "quick_en": "SMP does not regrow hair, but it can create the look of density or a shaved scalp. It is often useful when transplant coverage is limited or scars need camouflage.",
        "quick_ru": "SMP не выращивает волосы, но может создать видимость плотности или коротко выбритой головы. Метод часто полезен, когда пересадка ограничена или нужно замаскировать рубцы.",
        "cta_en": "Compare SMP and transplant options in Grafto.",
        "cta_ru": "Сравните SMP и пересадку волос в Grafto.",
    },
}


def json_ld(data: object) -> str:
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def strip_tags(value: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", value)).strip()


def extract_attr(fragment: str, attr: str) -> str:
    match = re.search(rf'{attr}="([^"]+)"', fragment)
    return html.unescape(match.group(1)) if match else ""


def parse_article_index() -> dict[str, list[ArticleCard]]:
    source = (ROOT / "articles" / "index.html").read_text(encoding="utf-8")
    grouped: dict[str, list[ArticleCard]] = {}
    for section_match in re.finditer(
        r'<section class="article-index-section" id="([^"]+)">(.*?)(?=</section><section class="article-index-section"|</section>\s*</main>)',
        source,
        re.S,
    ):
        cluster = section_match.group(1)
        section = section_match.group(2)
        cards: list[ArticleCard] = []
        for card_match in re.finditer(r'<div class="article-index-card">(.*?)</div>', section, re.S):
            card = card_match.group(1)
            en_link = re.search(r'<a href="([^"]+)" data-lang="en"><strong>(.*?)</strong></a>', card, re.S)
            ru_link = re.search(r'<a href="([^"]+)" data-lang="ru"[^>]*><strong>(.*?)</strong></a>', card, re.S)
            en_excerpt = re.search(r'<span class="article-index-card__secondary" data-lang="en">(.*?)</span>', card, re.S)
            ru_excerpt = re.search(r'<span class="article-index-card__secondary" data-lang="ru"[^>]*>(.*?)</span>', card, re.S)
            if not en_link or not ru_link:
                continue
            slug = en_link.group(1).strip("/").split("/")[-1]
            cards.append(
                ArticleCard(
                    slug=slug,
                    title_en=strip_tags(en_link.group(2)),
                    title_ru=strip_tags(ru_link.group(2)),
                    excerpt_en=strip_tags(en_excerpt.group(1)) if en_excerpt else "",
                    excerpt_ru=strip_tags(ru_excerpt.group(1)) if ru_excerpt else "",
                )
            )
        grouped[cluster] = cards
    return grouped


def page_header(prefix: str, lang: str, en_href: str | None = None, ru_href: str | None = None) -> str:
    home_href = f"{prefix}{lang}/"
    en_href = en_href or f"{prefix}en/"
    ru_href = ru_href or f"{prefix}ru/"
    guides_label = "Guides" if lang == "en" else "Материалы"
    app_label = "App" if lang == "en" else "Приложение"
    home_label = "Home" if lang == "en" else "Главная"
    return f"""<header class="article-topbar">
    <a href="{home_href}" class="article-logo" aria-label="Grafto home">
      <img src="{prefix}logo.jpg" alt="Grafto" width="32" height="32">
      <span>Grafto</span>
    </a>
    <nav class="article-topbar__nav" aria-label="Page navigation">
      <a href="{home_href}">{home_label}</a>
      <a href="{prefix}articles/?lang={lang}">{guides_label}</a>
      <a href="{prefix}app/?lang={lang}">{app_label}</a>
      <a href="{en_href}" class="{'active' if lang == 'en' else ''}">EN</a>
      <a href="{ru_href}" class="{'active' if lang == 'ru' else ''}">RU</a>
    </nav>
  </header>"""


def language_home(lang: str) -> str:
    is_ru = lang == "ru"
    other = "en" if is_ru else "ru"
    title = "Grafto — Platform for Hair Restoration Decisions" if not is_ru else "Grafto — платформа для решения о восстановлении волос"
    desc = (
        "Grafto helps you understand hair loss stage, graft and cost ranges, SMP tradeoffs, clinic questions, and preparation before booking a consultation."
        if not is_ru
        else "Grafto помогает понять стадию выпадения волос, диапазон графтов и стоимости, сравнить пересадку с SMP и подготовить вопросы к клинике до записи."
    )
    hero = (
        "Know your stage, graft range, cost, and clinic questions before booking"
        if not is_ru
        else "Узнайте стадию, диапазон графтов, стоимость и вопросы к клинике до записи"
    )
    summary = (
        "Grafto turns scattered research into a clearer decision path: assess your stage, estimate grafts and budget, compare transplant with SMP, and prepare for safer clinic conversations."
        if not is_ru
        else "Grafto превращает разрозненный поиск в понятный путь: оцените стадию, прикиньте графты и бюджет, сравните пересадку с SMP и подготовьтесь к более безопасному разговору с клиникой."
    )
    badge = "Hair restoration decision platform" if not is_ru else "Платформа для принятия решения о восстановлении волос"
    app_button = "Download Grafto" if not is_ru else "Скачать Grafto"
    guides_button = "Explore Guides" if not is_ru else "Все гайды"
    hub_title = "Topic hubs" if not is_ru else "Тематические разделы"
    trust_title = "How Grafto protects trust" if not is_ru else "Как Grafto защищает доверие"
    proof_title = "Built around the real decision" if not is_ru else "Построено вокруг реального решения"
    proof_summary = (
        "Understand the likely stage, compare clinic information, read practical guides, keep notes, and learn from patient stories in one place."
        if not is_ru
        else "Поймите вероятную стадию, сравните информацию о клиниках, читайте понятные материалы, сохраняйте заметки и смотрите истории пациентов в одном месте."
    )
    hub_cards = "\n".join(
        f"""<a class="cluster-card" href="./{meta['path']}/">{html.escape(meta['label_ru' if is_ru else 'label_en'])}</a>"""
        for meta in HUBS.values()
    )
    trust_cards = [
        (
            "Methodology",
            "Методология",
            "We use current AI models to gather and compare market information, then manually check claims before turning them into user-facing guidance.",
            "Мы используем современные ИИ-модели, чтобы собирать и сравнивать рыночную информацию, а затем вручную проверяем выводы перед публикацией рекомендаций.",
            "../trust/methodology/?lang=" + lang,
        ),
        (
            "Clinic review process",
            "Проверка клиник",
            "Clinics can apply for review, but listing is not guaranteed. Reputation, real results, testimonials, doctor credentials, certificates, and aftercare matter.",
            "Клиники могут подать заявку, но размещение не гарантировано. Важны репутация, реальные результаты, отзывы, квалификация врачей, сертификаты и сопровождение.",
            "../trust/clinic-reviews/?lang=" + lang,
        ),
        (
            "Limits",
            "Ограничения",
            "Grafto is informational. Final diagnosis and treatment planning should be made with a qualified surgeon.",
            "Grafto носит информационный характер. Итоговый диагноз и план лечения должен определять квалифицированный хирург.",
            "../trust/limitations/?lang=" + lang,
        ),
    ]
    trust_markup = "\n".join(
        f"""<div class="trust-item">
          <h3>{html.escape(ru if is_ru else en)}</h3>
          <p>{html.escape(ru_text if is_ru else en_text)}</p>
          <a class="trust-item__link" href="{href}">{'Read more' if not is_ru else 'Подробнее'}</a>
        </div>"""
        for en, ru, en_text, ru_text, href in trust_cards
    )
    screenshots = (
        [("../assets/screenshots/en-3.jpg?v=20260505c", "Grafto patient stories"), ("../assets/screenshots/en-1.jpg?v=20260505c", "Grafto stage assessment"), ("../assets/screenshots/en-5.jpg?v=20260505c", "Grafto guide screen"), ("../assets/screenshots/en-6.jpg?v=20260505c", "Grafto notes")]
        if not is_ru
        else [("../assets/screenshots/ru-4.jpg?v=20260505c", "Истории пациентов в Grafto"), ("../assets/screenshots/ru-6.jpg?v=20260505c", "Оценка стадии в Grafto"), ("../assets/screenshots/ru-2.jpg?v=20260505c", "Гайд в Grafto"), ("../assets/screenshots/ru-1.jpg?v=20260505c", "Заметки в Grafto")]
    )
    screenshot_markup = "\n".join(f'<img src="{src}" alt="{html.escape(alt)}" width="520" height="1125" loading="lazy">' for src, alt in screenshots)
    canonical = f"{SITE_URL}/{lang}/"
    alternate = f"{SITE_URL}/{other}/"
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebPage",
                "@id": canonical + "#webpage",
                "url": canonical,
                "name": title,
                "description": desc,
                "inLanguage": lang,
                "isPartOf": {"@type": "WebSite", "name": "Grafto", "url": SITE_URL + "/"},
                "mainEntity": {"@id": SITE_URL + "/app/#grafto-app"},
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Grafto", "item": canonical},
                ],
            },
        ],
    }
    return f"""<!DOCTYPE html>
<html lang="{lang}" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(desc)}">
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
  <link rel="canonical" href="{canonical}">
  <link rel="alternate" hreflang="en" href="{SITE_URL}/en/">
  <link rel="alternate" hreflang="ru" href="{SITE_URL}/ru/">
  <link rel="alternate" hreflang="x-default" href="{SITE_URL}/">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Grafto">
  <meta property="og:title" content="{html.escape(title)}">
  <meta property="og:description" content="{html.escape(desc)}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{SITE_URL}/hero.png">
  <script type="application/ld+json">{json_ld(schema)}</script>
  <link rel="stylesheet" href="../base.css">
  <link rel="stylesheet" href="../style.css?v={STYLE_VERSION}">
  <link rel="icon" href="../logo.jpg" type="image/jpeg">
</head>
<body class="article-page seo-home">
  {page_header('../', lang, '../en/', '../ru/')}
  <main class="article-index-shell">
    <section class="seo-hero">
      <p class="article-eyebrow">{html.escape(badge)}</p>
      <h1>{html.escape(hero)}</h1>
      <p>{html.escape(summary)}</p>
      <div class="hero__actions">
        <a href="{APP_URL}" target="_blank" rel="noopener noreferrer" class="btn btn--primary">{html.escape(app_button)}</a>
        <a href="../articles/?lang={lang}" class="btn btn--secondary">{html.escape(guides_button)}</a>
      </div>
    </section>
    <section class="article-index-section">
      <div class="section__header">
        <h2 class="section__title">{html.escape(hub_title)}</h2>
        <p class="section__subtitle">{html.escape(HUBS['cost']['quick_ru' if is_ru else 'quick_en'])}</p>
      </div>
      <div class="cluster-grid">{hub_cards}</div>
    </section>
    <section class="article-index-section">
      <div class="section__header">
        <h2 class="section__title">{html.escape(trust_title)}</h2>
      </div>
      <div class="trust-list">{trust_markup}</div>
    </section>
    <section class="article-index-section">
      <div class="section__header">
        <h2 class="section__title">{html.escape(proof_title)}</h2>
        <p class="section__subtitle">{html.escape(proof_summary)}</p>
      </div>
      <div class="screenshot-grid screenshot-grid--aligned">{screenshot_markup}</div>
    </section>
  </main>
</body>
</html>
"""


def hub_page(lang: str, cluster_key: str, cards: list[ArticleCard]) -> str:
    meta = HUBS[cluster_key]
    is_ru = lang == "ru"
    other = "en" if is_ru else "ru"
    title = meta["title_ru" if is_ru else "title_en"]
    desc = meta["description_ru" if is_ru else "description_en"]
    quick = meta["quick_ru" if is_ru else "quick_en"]
    cta = meta["cta_ru" if is_ru else "cta_en"]
    canonical = f"{SITE_URL}/{lang}/{meta['path']}/"
    alternate = f"{SITE_URL}/{other}/{meta['path']}/"
    label = meta["label_ru" if is_ru else "label_en"]
    article_cards = "\n".join(
        f"""<a class="article-index-card" href="../../articles/{lang}/{card.slug}/">
          <span class="article-index-card__cluster">{html.escape(label)}</span>
          <strong>{html.escape(card.title_ru if is_ru else card.title_en)}</strong>
          <span class="article-index-card__secondary">{html.escape(card.excerpt_ru if is_ru else card.excerpt_en)}</span>
        </a>"""
        for card in cards
    )
    facts = [
        ("Best use", "Лучше всего подходит", "Compare options before a clinic quote anchors your decision.", "Сравнить варианты до того, как предложение клиники станет якорем."),
        ("Decision risk", "Главный риск", "Choosing too quickly from one clinic, one price, or one before/after example.", "Слишком быстро выбрать по одной клинике, одной цене или одному фото до/после."),
        ("Grafto CTA", "CTA в Grafto", cta, cta),
    ]
    fact_rows = "\n".join(
        f"<tr><th>{html.escape(ru if is_ru else en)}</th><td>{html.escape(ru_text if is_ru else en_text)}</td></tr>"
        for en, ru, en_text, ru_text in facts
    )
    related = "\n".join(
        f"""<a class="cluster-card" href="../{other_meta['path']}/">{html.escape(other_meta['label_ru' if is_ru else 'label_en'])}</a>"""
        for key, other_meta in HUBS.items()
        if key != cluster_key
    )
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "CollectionPage",
                "@id": canonical + "#webpage",
                "url": canonical,
                "name": title,
                "description": desc,
                "inLanguage": lang,
                "isPartOf": {"@type": "WebSite", "name": "Grafto", "url": SITE_URL + "/"},
                "about": [{"@type": "Thing", "name": label}],
            },
            {
                "@type": "ItemList",
                "name": title,
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": index + 1,
                        "name": card.title_ru if is_ru else card.title_en,
                        "url": f"{SITE_URL}/articles/{lang}/{card.slug}/",
                    }
                    for index, card in enumerate(cards)
                ],
            },
            {
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": "What is this guide cluster for?" if not is_ru else "Для чего этот раздел?",
                        "acceptedAnswer": {"@type": "Answer", "text": quick},
                    },
                    {
                        "@type": "Question",
                        "name": "What should I do next?" if not is_ru else "Что делать дальше?",
                        "acceptedAnswer": {"@type": "Answer", "text": cta},
                    },
                ],
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Grafto", "item": f"{SITE_URL}/{lang}/"},
                    {"@type": "ListItem", "position": 2, "name": label, "item": canonical},
                ],
            },
        ],
    }
    return f"""<!DOCTYPE html>
<html lang="{lang}" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(title)} | Grafto</title>
  <meta name="description" content="{html.escape(desc)}">
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
  <link rel="canonical" href="{canonical}">
  <link rel="alternate" hreflang="en" href="{SITE_URL}/en/{meta['path']}/">
  <link rel="alternate" hreflang="ru" href="{SITE_URL}/ru/{meta['path']}/">
  <link rel="alternate" hreflang="x-default" href="{SITE_URL}/en/{meta['path']}/">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Grafto">
  <meta property="og:title" content="{html.escape(title)} | Grafto">
  <meta property="og:description" content="{html.escape(desc)}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{SITE_URL}/hero.png">
  <script type="application/ld+json">{json_ld(schema)}</script>
  <link rel="stylesheet" href="../../base.css">
  <link rel="stylesheet" href="../../style.css?v={STYLE_VERSION}">
  <link rel="icon" href="../../logo.jpg" type="image/jpeg">
</head>
<body class="article-page cluster-hub-page">
  {page_header('../../', lang, f"../../en/{meta['path']}/", f"../../ru/{meta['path']}/")}
  <main class="article-index-shell">
    <section class="article-index-hero">
      <p class="article-eyebrow">{html.escape(label)}</p>
      <h1>{html.escape(title)}</h1>
      <p><strong>{"Quick answer" if not is_ru else "Короткий ответ"}:</strong> {html.escape(quick)}</p>
    </section>
    <section class="article-index-section">
      <div class="article-plain-summary">
        <h2>{"How to use this cluster" if not is_ru else "Как пользоваться разделом"}</h2>
        <table class="seo-table"><tbody>{fact_rows}</tbody></table>
      </div>
    </section>
    <section class="article-index-section">
      <div class="section__header">
        <h2 class="section__title">{"Guides in this cluster" if not is_ru else "Материалы раздела"}</h2>
        <p class="section__subtitle">{html.escape(cta)}</p>
      </div>
      <div class="article-index-grid">{article_cards}</div>
    </section>
    <section class="article-index-section">
      <div class="section__header">
        <h2 class="section__title">{"Related clusters" if not is_ru else "Связанные разделы"}</h2>
      </div>
      <div class="cluster-grid">{related}</div>
    </section>
    <div class="article-final-cta">
      <p>{html.escape(cta)}</p>
      <a href="{APP_URL}" target="_blank" rel="noopener noreferrer" class="btn btn--primary">{"Open Grafto App" if not is_ru else "Открыть Grafto"}</a>
    </div>
  </main>
</body>
</html>
"""


def write_pages(grouped: dict[str, list[ArticleCard]]) -> None:
    for lang in ("en", "ru"):
        lang_dir = ROOT / lang
        lang_dir.mkdir(exist_ok=True)
        (lang_dir / "index.html").write_text(language_home(lang), encoding="utf-8")
        for key, meta in HUBS.items():
            target = lang_dir / meta["path"]
            target.mkdir(parents=True, exist_ok=True)
            (target / "index.html").write_text(hub_page(lang, key, grouped.get(key, [])), encoding="utf-8")


def add_url(root: ET.Element, url: str, priority: str, alternates: list[tuple[str, str]]) -> None:
    ns = "http://www.sitemaps.org/schemas/sitemap/0.9"
    xhtml = "http://www.w3.org/1999/xhtml"
    node = ET.SubElement(root, f"{{{ns}}}url")
    ET.SubElement(node, f"{{{ns}}}loc").text = url
    ET.SubElement(node, f"{{{ns}}}lastmod").text = LASTMOD
    ET.SubElement(node, f"{{{ns}}}changefreq").text = "weekly"
    ET.SubElement(node, f"{{{ns}}}priority").text = priority
    for hreflang, href in alternates:
        ET.SubElement(node, f"{{{xhtml}}}link", {"rel": "alternate", "hreflang": hreflang, "href": href})


def update_sitemap() -> None:
    sitemap_path = ROOT / "sitemap.xml"
    ET.register_namespace("", "http://www.sitemaps.org/schemas/sitemap/0.9")
    ET.register_namespace("xhtml", "http://www.w3.org/1999/xhtml")
    tree = ET.parse(sitemap_path)
    root = tree.getroot()
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    managed = {
        f"{SITE_URL}/en/",
        f"{SITE_URL}/ru/",
        f"{SITE_URL}/trust/methodology/",
    }
    for lang in ("en", "ru"):
        for meta in HUBS.values():
            managed.add(f"{SITE_URL}/{lang}/{meta['path']}/")
    for node in list(root.findall("sm:url", ns)):
        loc = node.find("sm:loc", ns)
        if loc is not None and loc.text in managed:
            root.remove(node)
            continue
        if loc is not None and loc.text == f"{SITE_URL}/?lang=ru":
            root.remove(node)
            continue
        if loc is not None and loc.text == f"{SITE_URL}/":
            lastmod = node.find("sm:lastmod", ns)
            if lastmod is None:
                lastmod = ET.SubElement(node, "{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod")
            lastmod.text = LASTMOD
            # Root remains the auto-detect / x-default entry; static language URLs are canonical alternates.
            for link in list(node):
                if link.tag.endswith("link"):
                    node.remove(link)
            for hreflang, href in (
                ("en", f"{SITE_URL}/en/"),
                ("en-US", f"{SITE_URL}/en/"),
                ("en-GB", f"{SITE_URL}/en/"),
                ("ru", f"{SITE_URL}/ru/"),
                ("ru-RU", f"{SITE_URL}/ru/"),
                ("ru-BY", f"{SITE_URL}/ru/"),
                ("x-default", f"{SITE_URL}/"),
            ):
                ET.SubElement(node, "{http://www.w3.org/1999/xhtml}link", {"rel": "alternate", "hreflang": hreflang, "href": href})
    add_url(
        root,
        f"{SITE_URL}/en/",
        "0.95",
        [("en", f"{SITE_URL}/en/"), ("ru", f"{SITE_URL}/ru/"), ("x-default", f"{SITE_URL}/")],
    )
    add_url(
        root,
        f"{SITE_URL}/ru/",
        "0.95",
        [("en", f"{SITE_URL}/en/"), ("ru", f"{SITE_URL}/ru/"), ("x-default", f"{SITE_URL}/")],
    )
    for meta in HUBS.values():
        add_url(
            root,
            f"{SITE_URL}/en/{meta['path']}/",
            "0.75",
            [("en", f"{SITE_URL}/en/{meta['path']}/"), ("ru", f"{SITE_URL}/ru/{meta['path']}/"), ("x-default", f"{SITE_URL}/en/{meta['path']}/")],
        )
        add_url(
            root,
            f"{SITE_URL}/ru/{meta['path']}/",
            "0.75",
            [("en", f"{SITE_URL}/en/{meta['path']}/"), ("ru", f"{SITE_URL}/ru/{meta['path']}/"), ("x-default", f"{SITE_URL}/en/{meta['path']}/")],
        )
    add_url(
        root,
        f"{SITE_URL}/trust/methodology/",
        "0.7",
        [("en", f"{SITE_URL}/trust/methodology/?lang=en"), ("ru", f"{SITE_URL}/trust/methodology/?lang=ru"), ("x-default", f"{SITE_URL}/trust/methodology/")],
    )
    ET.indent(tree, space="  ")
    tree.write(sitemap_path, encoding="utf-8", xml_declaration=True)


def main() -> None:
    grouped = parse_article_index()
    write_pages(grouped)
    update_sitemap()
    print("Generated localized SEO pages and cluster hubs.")
    for key, cards in grouped.items():
        print(key, len(cards))


if __name__ == "__main__":
    main()
