"""Time-of-day creative Telegram job templates — rotates layout per job."""
import hashlib
from datetime import datetime, timedelta

IST = timedelta(hours=5, minutes=30)

BRANDS = {
    "tax": {"label": "US Tax Jobs", "icon": "💼", "spark": "🇺🇸"},
    "testing": {"label": "Tax Software QA", "icon": "🧪", "spark": "⚗️"},
    "mortgage": {"label": "Mortgage & Loan", "icon": "🏠", "spark": "🏦"},
}

# Morning → Night themes (IST)
TIME_SLOTS = [
    (8, 11, "morning", "🌅 Good Morning Hire!", "☀️🟡✨", "╭━━━ 🌞 MORNING DROP 🌞 ━━━╮"),
    (12, 15, "afternoon", "🌞 Afternoon Alert!", "🔥🟠💫", "▰▰▰ 🔥 HOT JOB 🔥 ▰▰▰"),
    (16, 18, "afternoon", "⚡ Evening Rush!", "💥🟠⭐", "━━━ ⚡ FRESH OPENING ⚡ ━━━"),
    (19, 21, "evening", "🌆 Evening Opportunity!", "🌇🟣✨", "✦ ─── ✦ ─── ✦ ─── ✦"),
    (22, 23, "night", "🌙 Night Opening!", "🌙💎🔵", "◇ ─── ◇ ─── ◇ ─── ◇"),
]


def _ist_hour():
    return (datetime.utcnow() + IST).hour


def _theme():
    h = _ist_hour()
    for start, end, slot, vibe, mood, divider in TIME_SLOTS:
        if start <= h <= end:
            return {"slot": slot, "vibe": vibe, "mood": mood, "divider": divider}
    return {
        "slot": "default",
        "vibe": "🔥 Fresh Job Alert!",
        "mood": "🔥✨",
        "divider": "━━━━━━━━━━━━━━━━━━━━",
    }


def _variant(job, n=5):
    key = f"{job.get('title', '')}|{job.get('company', '')}|{_ist_hour()}"
    return int(hashlib.md5(key.encode()).hexdigest(), 16) % n


def render_job_post(
    brand_key,
    job,
    escape,
    company,
    title,
    location,
    experience,
    qualification,
    posted_str,
    url,
    source="",
    posted_today=False,
    salary="",
):
    brand = BRANDS[brand_key]
    t = _theme()
    v = _variant(job)
    co, ti, lo = escape(company), escape(title), escape(location)
    ex = escape(experience) if experience else ""
    qu = escape(qualification) if qualification else ""
    ps = escape(posted_str) if posted_str else ""

    ctas = [
        "👇👇 *Tap link below to apply* 👇👇",
        "👉👉 *Click below & apply now* 👉👉",
        "⬇️⬇️ *Apply link — scroll down* ⬇️⬇️",
        "👇 *Don't wait — apply below!* 👇",
        "🔗 *Apply here ↓*",
    ]
    cta = ctas[v % len(ctas)]

    header = f"🔥🔥 *{co}* 🔥🔥"
    role_line = f"💼 *Role:*\n*{ti}*"
    loc_line = f"📍 *Location:*\n*{lo}*"

    extras = []
    if ex:
        extras.append(f"👨‍💻 *Experience:* {ex}")
    if qu:
        extras.append(f"🎓 *Qualification:* {qu}")
    if ps:
        extras.append(f"⏰ *Posted:* {ps}")
    if salary and salary.lower() not in ("not mentioned", ""):
        extras.append(f"💰 *Salary:* {escape(salary)}")
    extra = "\n".join(extras)

    top = f"🚨 *Posted Today!* 🚨\n\n" if posted_today else ""
    apply = f"\n{cta}\n\n🔗 {url}"
    if source:
        apply += f"\n\n📋 _via {escape(source)}_"

    if v == 0:
        body = [
            top + t["mood"],
            t["vibe"],
            header,
            t["divider"],
            role_line,
            loc_line,
            extra,
            apply,
        ]
    elif v == 1:
        body = [
            top + f"✨ *{t['vibe']}* ✨",
            f"{brand['icon']} _{brand['label']}_ {brand['spark']}",
            header,
            "",
            role_line.replace("💼", "🎯"),
            loc_line,
            extra,
            apply,
        ]
    elif v == 2:
        body = [
            top + t["divider"],
            header,
            f"▸ *Role* → *{ti}*",
            f"▸ *Location* → *{lo}*",
            extra,
            apply,
        ]
    elif v == 3:
        body = [
            top + t["mood"],
            f"🏢 *{co}* {brand['spark']}🔥",
            "┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈",
            f"💼 *{ti}*",
            f"📍 *{lo}*",
            extra,
            apply,
        ]
    else:
        body = [
            top + f"⭐ *{t['vibe']}* ⭐",
            header,
            t["divider"],
            role_line,
            loc_line,
            extra,
            apply,
        ]

    return "\n".join(x for x in body if x)
