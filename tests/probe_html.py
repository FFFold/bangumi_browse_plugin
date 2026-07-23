"""探针 v5：检查 blog 页面和 calendar 详细结构。"""
import asyncio
import httpx
from bs4 import BeautifulSoup, Tag


async def probe():
    async with httpx.AsyncClient(
        proxy="http://127.0.0.1:7897",
        headers={"User-Agent": "Fold/bangumi-test"},
        timeout=20,
        follow_redirects=True,
    ) as c:
        # Blog detail page
        print("=== BLOG DETAIL ===")
        r = await c.get("https://bgm.tv/blog/373868")
        soup = BeautifulSoup(r.text, "lxml")

        # Content area
        for el_id in ["columnInSubjectA", "columnEpA", "columnBlogA", "columnMain"]:
            el = soup.select_one(f"#{el_id}")
            if el:
                print(f"  #{el_id}: {el.get_text(strip=True)[:300]}")

        # Title
        for sel in ["h1", "h2.title", ".blogTitle"]:
            el = soup.select_one(sel)
            if el:
                print(f"  {sel}: {el.get_text(strip=True)[:200]}")

        # Content
        for sel in [".entry", "article", ".message", ".blog_content", ".content"]:
            el = soup.select_one(sel)
            if el:
                print(f"  {sel}: text length={len(el.get_text(strip=True))}")
                print(f"    first 300: {el.get_text(strip=True)[:300]}")

        # Author
        for sel in ["a.avatar", ".author", ".blogAuthor"]:
            el = soup.select_one(sel)
            if el:
                title = el.get("title", "")
                text = el.get_text(strip=True)
                print(f"  {sel}: title='{title}' text='{text}'")

        # Calendar detailed structure
        print("\n=== CALENDAR DETAILED ===")
        r = await c.get("https://bgm.tv/calendar")
        soup = BeautifulSoup(r.text, "lxml")
        weeks = soup.select(".BgmCalendar ul.large > li.week")
        print(f"  Weeks: {len(weeks)}")
        if weeks:
            week = weeks[0]
            for tag in week.descendants:
                if isinstance(tag, Tag) and tag.name in ["dt", "dd", "h3", "li", "a", "small", "em", "p"]:
                    cls = tag.get("class", "")
                    text = tag.get_text(strip=True)[:80]
                    href = tag.get("href", "")
                    info = f"href={href}" if href else ""
                    print(f"  {tag.name}.{' '.join(cls) if isinstance(cls, list) else cls}: {text} {info}")

        print("\n=== DONE ===")


if __name__ == "__main__":
    asyncio.run(probe())
