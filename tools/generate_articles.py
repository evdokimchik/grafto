from __future__ import annotations

import html
import json
import re
import shutil
import textwrap
import unicodedata
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path

from docx import Document


ROOT = Path(__file__).resolve().parents[1]
DOCS = [
    Path.home() / "Desktop" / "Grafto_Articles_10_Bilingual.docx",
    Path.home() / "Desktop" / "Grafto_Clusters2to5_27_Articles.docx",
]
SITE_URL = "https://start.grafto.hair"
APP_URL = "https://apps.apple.com/app/grafto-hair-transplant-smp/id6759666757"
STYLE_VERSION = "12"
LASTMOD = "2026-05-05"

LEGACY_ARTICLE_CLUSTERS = {
    "fue": "grafts",
    "fut": "grafts",
    "dhi": "grafts",
    "smp": "smp",
    "cost": "cost",
    "gender": "clinic",
    "clinic": "clinic",
    "norwood-article": "norwood",
    "prep": "clinic",
    "swelling": "clinic",
    "minoxidil": "clinic",
    "expectations": "clinic",
}


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


ARTICLE_OVERRIDES: dict[tuple[str, str], list["Block"]] = {
    (
        "hair-transplant-cost-in-belarus",
        "ru",
    ): [
        Block("Беларусь как вариант для пересадки волос", "Heading 2"),
        Block(
            "Беларусь редко называют первой страной, когда говорят о пересадке волос. Чаще люди сразу вспоминают Турцию, иногда Польшу, Чехию или Россию. Но если вы живете в Беларуси, России, Польше, Литве, Латвии или рядом, Минск может быть удобным вариантом: ближе ехать, проще приехать на консультацию и легче вернуться на осмотр после операции.",
            "",
        ),
        Block(
            "Главное - не выбирать клинику только потому, что она рядом или дешевле. Пересадка волос зависит не только от цены. Важно, кто будет делать операцию, как клиника оценивает донорскую зону, какие результаты она показывает и будет ли нормальная поддержка после процедуры.",
            "",
        ),
        Block("Сколько это может стоить", "Heading 2"),
        Block(
            "Точных открытых данных по Беларуси меньше, чем по Турции или крупным европейским рынкам. Поэтому цены лучше воспринимать как ориентир, а не как обещание. По региональным сравнениям пересадка волос в Беларуси может стоить примерно от $1 500 до $4 000. Итоговая сумма зависит от объема работы, метода и уровня клиники [1].",
            "",
        ),
        Block(
            "Небольшая коррекция линии роста волос обычно стоит заметно меньше, чем большая пересадка на макушку и переднюю зону. Например, 1 200-1 500 графтов - это один уровень бюджета, а 3 000-4 000 графтов - совсем другой. Графт - это маленькая группа волосков, которую забирают из донорской зоны и пересаживают туда, где волос не хватает.",
            "",
        ),
        Block("Что сильнее всего влияет на цену", "Heading 2"),
        Block(
            "Первый фактор - количество графтов. Чем больше зона облысения, тем больше графтов может понадобиться. Но больше не всегда значит лучше: если взять слишком много волос из донорской зоны, можно испортить ее внешний вид.",
            "",
        ),
        Block(
            "Второй фактор - метод. FUE обычно встречается чаще всего. DHI, если клиника его предлагает, может стоить дороже. Но название метода само по себе не гарантирует хороший результат. Важнее, насколько аккуратно работает команда и участвует ли врач в ключевых этапах.",
            "",
        ),
        Block(
            "Третий фактор - опыт хирурга и команды. Хорошая пересадка требует спокойной, точной работы: графты нужно правильно извлечь, сохранить, подготовить и посадить под правильным углом. Это не та процедура, где стоит выбирать только по самой низкой цене [2][3].",
            "",
        ),
        Block(
            "Четвертый фактор - что входит в стоимость. Иногда цена выглядит низкой, но отдельно оплачиваются анализы, лекарства, PRP, осмотры, перевязки или повторная консультация. Всегда просите клинику написать, что именно включено.",
            "",
        ),
        Block("Почему дешевая цена может быть нормальной, а может быть опасной", "Heading 2"),
        Block(
            "Более низкая цена не обязательно означает плохую клинику. В Беларуси ниже расходы на аренду, персонал и обслуживание, чем в Германии или Великобритании. Поэтому нормальная клиника может стоить дешевле западноевропейской.",
            "",
        ),
        Block(
            "Но слишком низкая цена должна насторожить. Если клиника обещает очень много графтов за минимальные деньги, не объясняет план, не показывает врача, не оценивает донорскую зону и торопит с предоплатой - это плохой знак. Экономия на пересадке может потом стоить дороже, потому что донорская зона ограничена и ее нельзя просто восстановить заново.",
            "",
        ),
        Block("Что должно быть в нормальной консультации", "Heading 2"),
        Block(
            "Хорошая консультация не должна начинаться с фразы: \"Вам нужно 4 000 графтов, вносите депозит\". Сначала клиника должна понять вашу ситуацию: возраст, тип выпадения волос, стадию по шкале Норвуда, состояние донорской зоны, ожидания и историю лечения.",
            "",
        ),
        Block(
            "В идеале врач или специалист смотрит кожу головы, оценивает плотность донорской зоны и объясняет, какой результат реалистичен. Иногда человеку лучше сначала стабилизировать выпадение волос, а не сразу идти на операцию. Иногда пересадка подходит, но нужно делать ее в несколько этапов.",
            "",
        ),
        Block("Какие вопросы задать клинике", "Heading 2"),
        Block("Кто именно будет делать извлечение и посадку графтов?", "List Bullet"),
        Block("Сколько графтов вы предлагаете и почему именно столько?", "List Bullet"),
        Block("Как вы проверяете донорскую зону?", "List Bullet"),
        Block("Какие фото результатов можно посмотреть: до, сразу после и через 6-12 месяцев?", "List Bullet"),
        Block("Что входит в цену, а что оплачивается отдельно?", "List Bullet"),
        Block("Какие инструменты одноразовые, а какие стерилизуются?", "List Bullet"),
        Block("Что делать, если после операции возникнут вопросы или осложнения?", "List Bullet"),
        Block("Почему важна стерильность и последующий уход", "Heading 2"),
        Block(
            "Пересадка волос - это хирургическая процедура, пусть и под местной анестезией. Поэтому стерильность имеет значение. Нужно прямо спрашивать, как клиника обрабатывает инструменты, что используется один раз, а что стерилизуется между пациентами [6].",
            "",
        ),
        Block(
            "Также важен контакт после операции. Если вы делаете пересадку рядом с домом или в соседней стране, вам проще приехать на повторный осмотр. Это плюс Беларуси для людей из региона. Если что-то заживает не так, лучше иметь возможность быстро связаться с клиникой, а не решать все через переписку с другой стороны мира [4].",
            "",
        ),
        Block("Кому Беларусь может подойти", "Heading 2"),
        Block(
            "Беларусь может быть разумным вариантом, если вам важны понятный язык общения, близкая логистика, возможность приехать на осмотр и цена ниже, чем в Западной Европе. Особенно это актуально для людей из Беларуси, России, стран Балтии и Польши.",
            "",
        ),
        Block(
            "Но решение все равно нужно принимать по конкретной клинике, а не по стране. Сравните несколько вариантов, попросите письменный план, проверьте врача, посмотрите реальные примеры работ и не стесняйтесь задавать неудобные вопросы.",
            "",
        ),
        Block("Коротко", "Heading 2"),
        Block("Ориентир по цене в Беларуси: примерно $1 500-$4 000, но точная сумма зависит от количества графтов, метода и клиники.", "List Bullet"),
        Block("Минск может быть удобным вариантом для пациентов из Беларуси и соседних стран.", "List Bullet"),
        Block("Не выбирайте клинику только по цене. Важнее врач, план, донорская зона, стерильность и поддержка после операции.", "List Bullet"),
        Block("Очень дешевые предложения и обещания большого количества графтов без объяснений - повод насторожиться.", "List Bullet"),
        Block("Перед оплатой попросите письменный план: сколько графтов, каким методом, кто делает процедуру и что входит в стоимость.", "List Bullet"),
        Block("Источники", "Heading 2"),
        Block("[1] Оценка на основе данных medihair.com по России и региональных сравнений Восточной Европы: https://www.medihair.com/en/hair-transplant-russia/", ""),
        Block("[2] Akhyar, Y. et al. (2024). Техника FUE при андрогенетической алопеции. Bioscientia Medicina, 8(4). https://doi.org/10.37275/bsm.v8i4.962", ""),
        Block("[3] Vasudevan, B. et al. (2020). Исследование результатов FUE. Medical Journal Armed Forces India, 76(3). https://doi.org/10.1016/j.mjafi.2019.11.001", ""),
        Block("[4] Campbell, C. et al. (2025). Безопасность и результаты медицинского туризма в пластической хирургии. Plastic and Reconstructive Surgery - Global Open. https://doi.org/10.1097/GOX.0000000000007113", ""),
        Block("[5] tsilosaniclinic.com - Пересадка волос в Минске, Беларусь: https://tsilosaniclinic.com/hair-transplant-in-minsk-belarus/", ""),
        Block("[6] Kumar, A. & Jain, S. (2025). Стерильность инструментов при процедуре пересадки волос. SAGE Open Medicine. https://doi.org/10.1177/30499240251320904", ""),
    ],
}


@dataclass
class Article:
    number: int
    cluster: str
    slug: str
    en_title: str
    ru_title: str
    en_blocks: list[Block]
    ru_blocks: list[Block]


@dataclass
class Node:
    tag: str
    attrs: dict[str, str]
    children: list["Node | str"]


def clean(text: str) -> str:
    return " ".join(text.split())


RU_PLAIN_REPLACEMENTS = [
    (r"\bтрансплантация волос\b", "пересадка волос"),
    (r"\bтрансплантации волос\b", "пересадки волос"),
    (r"\bтрансплантацию волос\b", "пересадку волос"),
    (r"\bтрансплантацией волос\b", "пересадкой волос"),
    (r"\bтрансплантатами\b", "графтами"),
    (r"\bтрансплантатов\b", "графтов"),
    (r"\bтрансплантаты\b", "графты"),
    (r"\bтрансплантат\b", "графт"),
    (r"\bфолликулярных юнитов\b", "графтов"),
    (r"\bфолликулярные юниты\b", "графты"),
    (r"\bреципиентной зоны\b", "зоны пересадки"),
    (r"\bреципиентной зоне\b", "зоне пересадки"),
    (r"\bреципиентную зону\b", "зону пересадки"),
    (r"\bреципиентная зона\b", "зона пересадки"),
    (r"\bреципиентного участка\b", "участка пересадки"),
    (r"\bреципиентный участок\b", "участок пересадки"),
    (r"\bреципиентных участков\b", "участков, куда пересаживают волосы"),
    (r"\bреципиентные участки\b", "участки, куда пересаживают волосы"),
    (r"\bреципиентные каналы\b", "каналы для посадки графтов"),
    (r"\bнативного скальпа\b", "собственной кожи головы"),
    (r"\bнативные волосы\b", "свои волосы"),
    (r"\bскальпа\b", "кожи головы"),
    (r"\bскальп\b", "кожа головы"),
    (r"\bпредоперационная\b", "предварительная"),
    (r"\bпредоперационной\b", "предварительной"),
    (r"\bпредоперационную\b", "предварительную"),
    (r"\bпредоперационные\b", "предварительные"),
    (r"\bпредоперационных\b", "предварительных"),
    (r"\bпредоперационного\b", "предварительного"),
    (r"\bпослеоперационного ухода\b", "ухода после операции"),
    (r"\bпослеоперационный уход\b", "уход после операции"),
    (r"\bпослеоперационное наблюдение\b", "наблюдение после операции"),
    (r"\bпослеоперационные\b", "после операции"),
    (r"\bпослеоперационных\b", "после операции"),
    (r"\bпослеоперационном\b", "после операции"),
    (r"\bклинический процесс\b", "медицинская консультация"),
    (r"\bклинического опыта\b", "опыта работы с клиникой"),
    (r"\bклинической оценки\b", "оценки врача"),
    (r"\bклиническое обоснование\b", "медицинское объяснение"),
    (r"\bклинически уместно\b", "подходит по медицинским причинам"),
    (r"\bклинической честности\b", "честной работы клиники"),
    (r"\bинтраоперационной техникой\b", "тем, как проходит сама операция"),
    (r"\bнежелательных явлений\b", "осложнений"),
    (r"\bоптимальным\b", "лучшим"),
    (r"\bоптимальна\b", "лучше всего подходит"),
    (r"\bоптимальны\b", "лучше всего подходят"),
    (r"\bобусловленными\b", "связанными"),
    (r"\bобусловлен\b", "связан"),
    (r"\bобусловлена\b", "связана"),
    (r"\bнадлежащего\b", "правильного"),
    (r"\bнадлежащей\b", "правильной"),
    (r"\bнадлежащем\b", "правильном"),
    (r"\bнепрерывность\b", "постоянство"),
    (r"\bнепропорционально связаны\b", "часто связаны"),
    (r"\bмногофакторный характер\b", "зависит от многих факторов"),
    (r"\bпоказатель выживаемости\b", "приживаемость"),
    (r"\bжизнеспособность\b", "приживаемость"),
    (r"\bконтаминации\b", "загрязнения"),
    (r"\bавторитетных\b", "хороших"),
    (r"\bавторитетный\b", "хороший"),
    (r"\bустоявшихся\b", "проверенных"),
    (r"\bпровайдер\b", "клиника"),
    (r"\bпровайдера\b", "клинику"),
    (r"\bпровайдеров\b", "клиник"),
    (r"\bпровайдеры\b", "клиники"),
    (r"\bпациенты должны\b", "пациентам стоит"),
    (r"\bпациентам следует\b", "пациентам стоит"),
    (r"\bследует\b", "стоит"),
    (r"\bв конечном счёте\b", "в итоге"),
    (r"\bв значительной степени\b", "сильно"),
    (r"\bв ряде случаев\b", "иногда"),
    (r"\bкак правило\b", "обычно"),
    (r"\bсоответственно\b", "поэтому"),
    (r"\bданном этапе\b", "этой стадии"),
    (r"\bданного этапа\b", "этой стадии"),
    (r"\bпринимая во внимание\b", "учитывая"),
    (r"\bкожа головы-микропигментация\b", "SMP"),
    (r"\bв пересадки волос\b", "при пересадке волос"),
    (r"\bпри стандартной пересадки волос\b", "при стандартной пересадке волос"),
]

EN_PLAIN_REPLACEMENTS = [
    (r"\bhair transplantation\b", "hair transplant"),
    (r"\btransplantation\b", "transplant"),
    (r"\bfollicular units\b", "grafts"),
    (r"\brecipient area\b", "area where hair is placed"),
    (r"\brecipient zone\b", "area where hair is placed"),
    (r"\brecipient sites\b", "sites where grafts are placed"),
    (r"\bnative scalp\b", "original scalp"),
    (r"\bnative hair\b", "existing hair"),
    (r"\bpreoperative\b", "before-surgery"),
    (r"\bpre-operative\b", "before-surgery"),
    (r"\bpostoperative\b", "after-surgery"),
    (r"\bpost-operative\b", "after-surgery"),
    (r"\bintraoperative\b", "during-surgery"),
    (r"\bintra-operative\b", "during-surgery"),
    (r"\bclinical process\b", "medical consultation"),
    (r"\bclinical assessment\b", "doctor's assessment"),
    (r"\bclinical justification\b", "medical reason"),
    (r"\bclinically appropriate\b", "medically appropriate"),
    (r"\bprovider\b", "clinic"),
    (r"\bproviders\b", "clinics"),
    (r"\bmultifactorial\b", "affected by many things"),
    (r"\bgraft survival rate\b", "graft survival"),
    (r"\bviability\b", "survival"),
    (r"\bcontamination\b", "infection risk"),
    (r"\badverse events\b", "complications"),
    (r"\bsuboptimal\b", "poor"),
    (r"\bsubstantially\b", "much"),
    (r"\bsignificantly\b", "noticeably"),
    (r"\bin many cases\b", "often"),
    (r"\bas a result\b", "so"),
    (r"\btherefore\b", "so"),
    (r"\bnevertheless\b", "still"),
    (r"\bpatients should\b", "you should"),
    (r"\bpatients must\b", "you should"),
    (r"\bpatients need to\b", "you need to"),
]


def apply_replacements(text: str, replacements: list[tuple[str, str]]) -> str:
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


def soften_sentence_breaks(text: str, lang: str) -> str:
    if len(text) < 230:
        return text
    if lang == "ru":
        text = re.sub(r", однако ", ". Но ", text, flags=re.IGNORECASE)
        text = re.sub(r", поэтому ", ". Поэтому ", text, flags=re.IGNORECASE)
        text = re.sub(r", потому что ", ". Потому что ", text, flags=re.IGNORECASE)
        text = re.sub(r", что означает: ", ". Это значит: ", text, flags=re.IGNORECASE)
    else:
        text = re.sub(r", however,? ", ". But ", text, flags=re.IGNORECASE)
        text = re.sub(r", which means ", ". This means ", text, flags=re.IGNORECASE)
        text = re.sub(r", because ", ". Because ", text, flags=re.IGNORECASE)
    return text


def plain_language_text(text: str, lang: str) -> str:
    replacements = RU_PLAIN_REPLACEMENTS if lang == "ru" else EN_PLAIN_REPLACEMENTS
    text = apply_replacements(text, replacements)
    text = soften_sentence_breaks(text, lang)
    text = re.sub(r"\s+", " ", text).strip()
    text = text.replace("обычно,", "обычно")
    text = text.replace("typically,", "typically")
    text = text.replace("infection risk risks", "infection risks")
    text = text.replace("after-surgery care", "care after surgery")
    text = text.replace("after-surgery follow-up", "follow-up after surgery")
    text = text.replace("по пересадки волос", "по пересадке волос")
    text = text.replace("при пересадки волос", "при пересадке волос")
    text = text.replace("двусторонний медицинская консультация", "двусторонняя медицинская консультация")
    text = text.replace("центрального кожи головы", "центральной части кожи головы")
    text = text.replace("другого клинику", "другой клиники")
    text = text.replace("одного клинику", "одной клиники")
    text = text.replace("сторонних клиник медицинского финансирования", "сторонние сервисы медицинского финансирования")
    text = re.sub(r"\.\s+([а-я])", lambda m: ". " + m.group(1).upper(), text)
    text = re.sub(r"\.\s+(?!https?://)([a-z])", lambda m: ". " + m.group(1).upper(), text)
    if text and text[0].isalpha():
        text = text[0].upper() + text[1:]
    return text


def plain_language_blocks(blocks: list[Block], lang: str) -> list[Block]:
    plain: list[Block] = []
    for block in blocks:
        if block.style.startswith("Heading"):
            plain.append(block)
        else:
            plain.append(Block(plain_language_text(block.text, lang), block.style))
    return plain


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


class TreeBuilder(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = Node("document", {}, [])
        self.stack = [self.root]

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        node = Node(tag, {key: value or "" for key, value in attrs}, [])
        self.stack[-1].children.append(node)
        if tag not in {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}:
            self.stack.append(node)

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                break

    def handle_data(self, data: str) -> None:
        if data:
            self.stack[-1].children.append(data)


def has_class(node: Node, class_name: str) -> bool:
    return class_name in node.attrs.get("class", "").split()


def iter_nodes(node: Node):
    for child in node.children:
        if isinstance(child, Node):
            yield child
            yield from iter_nodes(child)


def text_content(node: Node) -> str:
    parts: list[str] = []
    for child in node.children:
        if isinstance(child, str):
            parts.append(child)
        else:
            parts.append(text_content(child))
    return clean(" ".join(parts))


def first_child_text(node: Node, tag: str) -> str:
    for child in iter_nodes(node):
        if child.tag == tag:
            return text_content(child)
    return ""


def content_for_lang(view: Node, lang: str) -> Node | None:
    for node in iter_nodes(view):
        if has_class(node, "article-view__content") and node.attrs.get("data-lang") == lang:
            return node
    return None


def blocks_from_content(node: Node) -> list[Block]:
    blocks: list[Block] = []

    def walk(current: Node) -> None:
        if has_class(current, "article-cta"):
            return
        if current.tag == "h2":
            return
        if current.tag == "h3":
            text = text_content(current)
            if text:
                blocks.append(Block(text, "Heading 2"))
            return
        if current.tag == "p":
            text = text_content(current)
            if text:
                blocks.append(Block(text, ""))
            return
        if current.tag == "li":
            text = text_content(current)
            if text:
                blocks.append(Block(text, "List Bullet"))
            return
        for child in current.children:
            if isinstance(child, Node):
                walk(child)

    walk(node)
    return blocks


def parse_legacy_articles() -> list[Article]:
    parser = TreeBuilder()
    parser.feed((ROOT / "index.html").read_text(encoding="utf-8"))
    articles: list[Article] = []
    for view in iter_nodes(parser.root):
        article_id = view.attrs.get("data-view")
        if not has_class(view, "article-view") or article_id not in LEGACY_ARTICLE_CLUSTERS:
            continue
        en_content = content_for_lang(view, "en")
        ru_content = content_for_lang(view, "ru")
        if en_content is None or ru_content is None:
            continue
        en_title = first_child_text(en_content, "h2")
        ru_title = first_child_text(ru_content, "h2")
        if not en_title:
            continue
        articles.append(
            Article(
                number=100 + len(articles),
                cluster=LEGACY_ARTICLE_CLUSTERS[article_id],
                slug=slugify(en_title),
                en_title=en_title,
                ru_title=ru_title or en_title,
                en_blocks=blocks_from_content(en_content),
                ru_blocks=blocks_from_content(ru_content),
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


def plain_summary_items(article: Article, lang: str) -> list[str]:
    title = article.ru_title if lang == "ru" else article.en_title
    if lang == "ru":
        if article.cluster == "cost":
            return [
                f"Эта страница простыми словами объясняет тему: {title}.",
                "Главные факторы цены: количество графтов, метод, участие врача, уровень клиники и то, что входит в пакет.",
                "Не сравнивайте только итоговую сумму. Сравнивайте план, врача, поддержку после операции и прозрачность цены.",
                "Перед оплатой попросите письменный план: сколько графтов, почему столько, кто делает процедуру и какие расходы могут быть отдельно.",
            ]
        if article.cluster == "grafts":
            return [
                "Графты - это маленькие группы волос, которые берут из донорской зоны и пересаживают туда, где волос не хватает.",
                "Нужное количество графтов зависит не от желания получить максимум, а от зоны потери, донорского запаса и долгосрочного плана.",
                "Слишком много графтов за один раз может повредить донорскую зону. Это один из главных рисков, о котором стоит спросить заранее.",
                "На консультации просите объяснить не только число графтов, но и почему это число безопасно именно для вас.",
            ]
        if article.cluster == "norwood":
            return [
                "Шкала Норвуда помогает примерно понять стадию мужского облысения, но не заменяет консультацию врача.",
                "Одна и та же стадия может выглядеть по-разному у разных людей: важны возраст, донорская зона, толщина волос и скорость выпадения.",
                "Чем выше стадия, тем важнее не обещать слишком много за один сеанс и заранее думать о будущем выпадении.",
                "Используйте статью как подготовку: сначала оцените стадию, потом обсуждайте графты, цену и реалистичный результат.",
            ]
        if article.cluster == "clinic":
            return [
                "Главная задача - понять, работает ли клиника в ваших интересах, а не просто продает процедуру.",
                "Хорошая клиника объясняет ограничения, показывает реальные результаты, называет врача и не давит срочными скидками.",
                "Плохой знак - обещания большого числа графтов без осмотра донорской зоны и без понятного плана.",
                "Сохраните вопросы из статьи и используйте их на консультации, чтобы сравнивать клиники спокойно и по одним критериям.",
            ]
        return [
            "SMP - это не пересадка волос, а имитация коротких волосков с помощью пигмента в коже головы.",
            "Метод может помочь при шрамах, diffuse thinning, неудачной пересадке или когда пересадка не подходит.",
            "Результат сильно зависит от мастера, цвета пигмента, формы линии роста и того, как заживает кожа.",
            "Перед процедурой уточните количество сеансов, стоимость коррекций, примеры работ и правила ухода после SMP.",
        ]

    if article.cluster == "cost":
        return [
            f"This page explains the topic in practical terms: {title}.",
            "The main price drivers are graft count, method, surgeon involvement, clinic quality, and what the package includes.",
            "Do not compare only the final number. Compare the plan, the doctor, aftercare, and whether the quote is transparent.",
            "Before paying, ask for a written plan: graft count, why that number, who performs the procedure, and what may cost extra.",
        ]
    if article.cluster == "grafts":
        return [
            "Grafts are small natural groups of hairs moved from the donor area to the thinning area.",
            "The right graft count depends on the area being treated, donor supply, hair quality, and long-term planning.",
            "More grafts are not always better. Taking too many can damage the donor area and limit future options.",
            "Use the article to ask why a suggested number is safe for you, not just whether it sounds impressive.",
        ]
    if article.cluster == "norwood":
        return [
            "The Norwood scale is a quick way to describe male hair loss stage, but it is not a full medical plan.",
            "The same stage can look different depending on age, donor density, hair thickness, and speed of loss.",
            "Higher stages need more careful planning because donor hair is limited and future loss still matters.",
            "Use this guide to prepare for a realistic conversation about grafts, cost, and expected result.",
        ]
    if article.cluster == "clinic":
        return [
            "The goal is to judge whether a clinic is helping you make a safe decision or simply selling a procedure.",
            "A good clinic explains limits, shows real results, names the doctor, and avoids pressure tactics.",
            "A warning sign is a large graft promise without examining the donor area or giving a clear plan.",
            "Use the questions in this article to compare clinics calmly, using the same criteria each time.",
        ]
    return [
        "SMP is not a hair transplant. It creates the look of tiny shaved hairs using pigment in the scalp.",
        "It can help with scars, diffuse thinning, failed transplants, or cases where surgery is not a good fit.",
        "The result depends heavily on the practitioner, pigment color, hairline design, and healing.",
        "Before booking, ask about sessions, touch-ups, pricing, real examples, and aftercare rules.",
    ]


def render_plain_summary(article: Article, lang: str) -> str:
    label = "Простыми словами" if lang == "ru" else "In plain language"
    items = "\n".join(f"        <li>{html.escape(item)}</li>" for item in plain_summary_items(article, lang))
    return f"""<section class="article-plain-summary" aria-label="{html.escape(label)}">
        <h2>{html.escape(label)}</h2>
        <ul>
{items}
        </ul>
      </section>"""


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


def render_faq_section(title: str, desc: str, lang: str) -> str:
    items = faq_items(title, desc, lang)
    details = []
    for index, (question, answer) in enumerate(items):
        open_attr = " open" if index == 0 else ""
        details.append(
            f"""        <details{open_attr}>
          <summary>{html.escape(question)}</summary>
          <p>{html.escape(answer)}</p>
        </details>"""
        )
    return f"""<section class="article-faq" aria-label="FAQ">
        <h2>FAQ</h2>
{chr(10).join(details)}
      </section>"""


def excerpt(blocks: list[Block]) -> str:
    for block in blocks:
        if block.style != "List Bullet" and not looks_like_heading(block.text, block.style):
            if len(block.text) <= 155:
                return block.text
            return block.text[:155].rsplit(" ", 1)[0].rstrip(".,;:") + "..."
    return ""


def word_count(blocks: list[Block]) -> int:
    text = " ".join(block.text for block in blocks)
    return len(re.findall(r"\w+", text, flags=re.UNICODE))


def json_ld(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def page_template(article: Article, lang: str) -> str:
    title = article.en_title if lang == "en" else article.ru_title
    other_title = article.ru_title if lang == "en" else article.en_title
    blocks = article.en_blocks if lang == "en" else article.ru_blocks
    cluster = CLUSTERS[article.cluster]
    cluster_label = cluster[lang]
    cta = cluster[f"cta_{lang}"]
    other_lang = "ru" if lang == "en" else "en"
    desc = excerpt(blocks)
    answer_summary = " ".join(plain_summary_items(article, lang)[:2])
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
    article_schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": desc,
        "inLanguage": lang,
        "articleSection": cluster_label,
        "wordCount": word_count(blocks),
        "datePublished": LASTMOD,
        "dateModified": LASTMOD,
        "mainEntityOfPage": {"@type": "WebPage", "@id": canonical},
        "url": canonical,
        "image": f"{SITE_URL}/hero.png",
        "author": {"@type": "Organization", "name": "Grafto", "url": SITE_URL},
        "publisher": {
            "@type": "Organization",
            "name": "Grafto",
            "url": SITE_URL,
            "logo": {"@type": "ImageObject", "url": f"{SITE_URL}/logo.jpg"},
        },
        "isAccessibleForFree": True,
    }
    breadcrumb_schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Grafto", "item": f"{SITE_URL}/"},
            {"@type": "ListItem", "position": 2, "name": back_label, "item": f"{SITE_URL}/articles/"},
            {"@type": "ListItem", "position": 3, "name": title, "item": canonical},
        ],
    }
    faq_schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": question,
                "acceptedAnswer": {"@type": "Answer", "text": answer},
            }
            for question, answer in faq_items(title, answer_summary, lang)
        ],
    }
    quick_label = "Короткий ответ" if lang == "ru" else "Quick answer"

    return f"""<!DOCTYPE html>
<html lang="{lang}" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(title)} | Grafto</title>
  <meta name="description" content="{html.escape(desc)}">
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
  <link rel="canonical" href="{canonical}">
  <link rel="alternate" hreflang="{lang}" href="{canonical}">
  <link rel="alternate" hreflang="{other_lang}" href="{alternate}">
  <link rel="alternate" hreflang="x-default" href="{SITE_URL}/articles/en/{article.slug}/">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="Grafto">
  <meta property="og:title" content="{html.escape(title)}">
  <meta property="og:description" content="{html.escape(desc)}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{SITE_URL}/hero.png">
  <meta property="article:section" content="{html.escape(cluster_label)}">
  <meta property="article:published_time" content="{LASTMOD}">
  <meta property="article:modified_time" content="{LASTMOD}">
  <meta name="twitter:card" content="summary_large_image">
  <script type="application/ld+json">{json_ld(article_schema)}</script>
  <script type="application/ld+json">{json_ld(breadcrumb_schema)}</script>
  <script type="application/ld+json">{json_ld(faq_schema)}</script>
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
      <a href="../../?lang={lang}">{back_label}</a>
      <a href="../../{other_lang}/{article.slug}/">{language_label}</a>
    </nav>
  </header>

  <main class="article-shell">
    <article class="article-content">
      <p class="article-eyebrow">{cluster_intro}: {html.escape(cluster_label)}</p>
      <h1>{html.escape(title)}</h1>
      <p class="article-summary"><strong>{html.escape(quick_label)}:</strong> {html.escape(answer_summary)}</p>
      <div class="article-disclaimer">{html.escape(disclaimer)}</div>
      {render_plain_summary(article, lang)}
      {render_blocks(blocks)}
      {render_faq_section(title, answer_summary, lang)}
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
            en_excerpt = excerpt(article.en_blocks)
            ru_excerpt = excerpt(article.ru_blocks)
            cards.append(
                f"""<div class="article-index-card">
          <span class="article-index-card__cluster" data-lang="en">{html.escape(cluster["en"])}</span>
          <span class="article-index-card__cluster" data-lang="ru" style="display:none">{html.escape(cluster["ru"])}</span>
          <a href="./en/{article.slug}/" data-lang="en"><strong>{html.escape(article.en_title)}</strong></a>
          <a href="./ru/{article.slug}/" data-lang="ru" style="display:none"><strong>{html.escape(article.ru_title)}</strong></a>
          <span class="article-index-card__secondary" data-lang="en">{html.escape(en_excerpt)}</span>
          <span class="article-index-card__secondary" data-lang="ru" style="display:none">{html.escape(ru_excerpt)}</span>
        </div>"""
            )
        sections.append(
            f"""<section class="article-index-section" id="{key}">
      <div class="section__header">
        <h2 class="section__title" data-lang="en">{html.escape(cluster["en"])}</h2>
        <h2 class="section__title" data-lang="ru" style="display:none">{html.escape(cluster["ru"])}</h2>
        <p class="section__subtitle" data-lang="en">{html.escape(cluster["cta_en"])}</p>
        <p class="section__subtitle" data-lang="ru" style="display:none">{html.escape(cluster["cta_ru"])}</p>
      </div>
      <div class="article-index-grid">
        {"".join(cards)}
      </div>
    </section>"""
        )

    item_list_schema = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "Hair Transplant and SMP Guides",
        "url": f"{SITE_URL}/articles/",
        "numberOfItems": len(articles),
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": index + 1,
                "name": article.en_title,
                "url": f"{SITE_URL}/articles/en/{article.slug}/",
            }
            for index, article in enumerate(articles)
        ],
    }
    web_page_schema = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "Hair Transplant and SMP Guides",
        "description": "Guides on hair transplant cost, graft counts, Norwood stages, clinic choice, and SMP from Grafto.",
        "url": f"{SITE_URL}/articles/",
        "inLanguage": ["en", "ru"],
        "isPartOf": {"@type": "WebSite", "name": "Grafto", "url": f"{SITE_URL}/"},
    }

    return f"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Hair Transplant and SMP Guides | Grafto</title>
  <meta name="description" content="Guides on hair transplant cost, graft counts, Norwood stages, clinic choice, and SMP from Grafto.">
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
  <link rel="canonical" href="{SITE_URL}/articles/">
  <link rel="alternate" hreflang="en" href="{SITE_URL}/articles/?lang=en">
  <link rel="alternate" hreflang="ru" href="{SITE_URL}/articles/?lang=ru">
  <link rel="alternate" hreflang="x-default" href="{SITE_URL}/articles/">
  <meta property="og:type" content="website">
  <meta property="og:title" content="Hair Transplant and SMP Guides | Grafto">
  <meta property="og:description" content="Guides organized by real patient decisions: cost, grafts, Norwood scale, clinic choice, and SMP.">
  <meta property="og:url" content="{SITE_URL}/articles/">
  <meta property="og:image" content="{SITE_URL}/hero.png">
  <script type="application/ld+json">{json_ld(web_page_schema)}</script>
  <script type="application/ld+json">{json_ld(item_list_schema)}</script>
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
      <a href="../?lang=en" data-lang="en">Home</a>
      <a href="../?lang=ru" data-lang="ru" style="display:none">Главная</a>
      <a href="{APP_URL}" target="_blank" rel="noopener noreferrer">App Store</a>
      <a href="?lang=en" data-lang-switch="en">EN</a>
      <a href="?lang=ru" data-lang-switch="ru">RU</a>
    </nav>
  </header>

  <main class="article-index-shell">
    <section class="article-index-hero">
      <p class="article-eyebrow" data-lang="en">Guides for making the right decision</p>
      <p class="article-eyebrow" data-lang="ru" style="display:none">Гайды для принятия правильного решения</p>
      <h1 data-lang="en">Hair Transplant and SMP Guides</h1>
      <h1 data-lang="ru" style="display:none">Гайды по пересадке волос и SMP</h1>
      <p data-lang="en">Dedicated pages for cost, graft ranges, Norwood stage, clinic choice, and SMP topics. Each guide is built to help users make better decisions before booking a consultation.</p>
      <p data-lang="ru" style="display:none">Отдельные страницы по стоимости, графтам, шкале Норвуда, выбору клиники и SMP. Каждый материал помогает принять более спокойное решение до консультации.</p>
    </section>
    {"".join(sections)}
  </main>
  <script>
  (function() {{
    const LANG_KEY = 'grafto_lang';
    const LANG_MANUAL_KEY = 'grafto_lang_manual';

    function browserLang() {{
      const langs = (navigator.languages && navigator.languages.length)
        ? navigator.languages
        : [navigator.language || navigator.userLanguage || 'en'];
      for (const l of langs) {{
        const raw = (l || '').toLowerCase();
        const code = raw.slice(0, 2);
        if (code === 'ru' || code === 'be' || code === 'uk' || code === 'kk' || code === 'ky') return 'ru';
        if (raw.startsWith('ru-')) return 'ru';
      }}
      return 'en';
    }}

    function detectLang() {{
      try {{
        const urlLang = new URLSearchParams(window.location.search).get('lang');
        if (urlLang === 'ru' || urlLang === 'en') return urlLang;
      }} catch (e) {{}}
      try {{
        const saved = localStorage.getItem(LANG_KEY);
        const manual = localStorage.getItem(LANG_MANUAL_KEY);
        if (manual === '1' && (saved === 'ru' || saved === 'en')) return saved;
      }} catch (e) {{}}
      return browserLang();
    }}

    function setLang(lang) {{
      document.documentElement.lang = lang === 'ru' ? 'ru' : 'en';
      document.querySelectorAll('[data-lang]').forEach(el => {{
        el.style.display = el.getAttribute('data-lang') === lang ? '' : 'none';
      }});
      document.querySelectorAll('[data-lang-switch]').forEach(el => {{
        el.classList.toggle('active', el.getAttribute('data-lang-switch') === lang);
      }});
      document.title = lang === 'ru'
        ? 'Гайды по пересадке волос и SMP | Grafto'
        : 'Hair Transplant and SMP Guides | Grafto';
    }}

    const lang = detectLang();
    setLang(lang);
    document.querySelectorAll('[data-lang-switch]').forEach(link => {{
      link.addEventListener('click', () => {{
        const nextLang = link.getAttribute('data-lang-switch');
        try {{
          localStorage.setItem(LANG_KEY, nextLang);
          localStorage.setItem(LANG_MANUAL_KEY, '1');
        }} catch (e) {{}}
      }});
    }});
  }})();
  </script>
</body>
</html>
"""


def update_sitemap(articles: list[Article]) -> None:
    sitemap_path = ROOT / "sitemap.xml"
    ET.register_namespace("", "http://www.sitemaps.org/schemas/sitemap/0.9")
    ET.register_namespace("xhtml", "http://www.w3.org/1999/xhtml")
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
        if loc is not None and (loc.text in url_set or "#" in (loc.text or "")):
            root.remove(node)
        elif loc is not None and loc.text in {f"{SITE_URL}/", f"{SITE_URL}/?lang=ru"}:
            lastmod = node.find("sm:lastmod", ns)
            if lastmod is None:
                lastmod = ET.SubElement(node, "{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod")
            lastmod.text = LASTMOD
    existing = {loc.text for loc in root.findall("sm:url/sm:loc", ns)}

    article_by_url: dict[str, tuple[Article, str]] = {}
    for article in articles:
        article_by_url[f"{SITE_URL}/articles/en/{article.slug}/"] = (article, "en")
        article_by_url[f"{SITE_URL}/articles/ru/{article.slug}/"] = (article, "ru")

    for url in urls:
        if url in existing:
            continue
        node = ET.SubElement(root, "{http://www.sitemaps.org/schemas/sitemap/0.9}url")
        loc = ET.SubElement(node, "{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
        loc.text = url
        lastmod = ET.SubElement(node, "{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod")
        lastmod.text = LASTMOD
        changefreq = ET.SubElement(node, "{http://www.sitemaps.org/schemas/sitemap/0.9}changefreq")
        changefreq.text = "monthly"
        priority = ET.SubElement(node, "{http://www.sitemaps.org/schemas/sitemap/0.9}priority")
        priority.text = "0.7" if url.endswith("/articles/") else "0.6"
        if url.endswith("/articles/"):
            for hreflang, href in (
                ("en", f"{SITE_URL}/articles/?lang=en"),
                ("ru", f"{SITE_URL}/articles/?lang=ru"),
                ("x-default", f"{SITE_URL}/articles/"),
            ):
                ET.SubElement(
                    node,
                    "{http://www.w3.org/1999/xhtml}link",
                    {"rel": "alternate", "hreflang": hreflang, "href": href},
                )
        elif url in article_by_url:
            article, _lang = article_by_url[url]
            for hreflang, href in (
                ("en", f"{SITE_URL}/articles/en/{article.slug}/"),
                ("ru", f"{SITE_URL}/articles/ru/{article.slug}/"),
                ("x-default", f"{SITE_URL}/articles/en/{article.slug}/"),
            ):
                ET.SubElement(
                    node,
                    "{http://www.w3.org/1999/xhtml}link",
                    {"rel": "alternate", "hreflang": hreflang, "href": href},
                )
    ET.indent(tree, space="  ")
    tree.write(sitemap_path, encoding="utf-8", xml_declaration=True)


def main() -> None:
    articles: list[Article] = []
    for doc in DOCS:
        articles.extend(parse_doc(doc))
    articles.extend(parse_legacy_articles())
    for article in articles:
        if (article.slug, "en") in ARTICLE_OVERRIDES:
            article.en_blocks = ARTICLE_OVERRIDES[(article.slug, "en")]
        if (article.slug, "ru") in ARTICLE_OVERRIDES:
            article.ru_blocks = ARTICLE_OVERRIDES[(article.slug, "ru")]
        article.en_blocks = plain_language_blocks(article.en_blocks, "en")
        article.ru_blocks = plain_language_blocks(article.ru_blocks, "ru")

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
