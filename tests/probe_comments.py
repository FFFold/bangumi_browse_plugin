"""探针：检查用户指定的剧集页面。"""
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
        # 1. 抓取用户指定的剧集页面
        print("=== EP 1696986 ===")
        r = await c.get("https://bgm.tv/ep/1696986")
        with open("ep_real.html", "w", encoding="utf-8") as f:
            f.write(r.text)
        soup = BeautifulSoup(r.text, "lxml")

        comment_list = soup.select_one("#comment_list")
        if comment_list:
            children = [c for c in comment_list.children if isinstance(c, Tag)]
            print(f"  #comment_list tag children: {len(children)}")
            for child in children[:10]:
                cls = " ".join(child.get("class", [])) if isinstance(child.get("class"), list) else child.get("class", "")
                print(f"    {child.name}.{cls}: {child.get_text(strip=True)[:120]}")
            if children:
                print(f"\n  First comment full HTML:\n{str(children[0])[:1000]}")

        # 2. 查找 comment_url 的具体值
        import re
        matches = re.findall(r"comment_url[^=]*=\s*['\"]([^'\"]+)['\"]\s*\+\s*['\"]?(\d+)['\"]?", r.text)
        print(f"\n  comment_url patterns: {matches}")

        # 3. 查找 topic 相关 JS 变量
        for var in ['topic_id', 'ep_id', 'subject_id', 'comment']:
            ms = re.findall(rf"{var}\s*=\s*(\d+)", r.text)
            if ms:
                print(f"  {var}: {ms}")

        # 4. 检查 JS 中加载评论的 URL 模式
        matches = re.findall(r'["\']([^"\']*(?:topic|comment|reply)[^"\']*\d+[^"\']*)["\']', r.text)
        print(f"  topic/comment URLs: {matches}")

        # 5. 之前找到的 subject comments 页面有内容
        print("\n=== SUBJECT 572458 COMMENTS (DETAILED) ===")
        r = await c.get("https://bgm.tv/subject/572458/comments")
        soup = BeautifulSoup(r.text, "lxml")
        # Check .item elements
        items = soup.select(".item")
        print(f"  .item count: {len(items)}")
        for i, item in enumerate(items[:3]):
            user_el = item.select_one("a.avatar, a.l, span.user")
            content_el = item.select_one(".reply_content, .message, .content, .text")
            time_el = item.select_one("small.greytext, .time, .date")
            print(f"  Item {i}: user={user_el.get('title', user_el.get_text(strip=True)) if user_el else 'N/A'}")
            print(f"    content: {(content_el.get_text(strip=True)[:150] + '...') if content_el and content_el.get_text(strip=True) else 'N/A'}")
            print(f"    time: {time_el.get_text(strip=True) if time_el else 'N/A'}")

        print("\n=== DONE ===")


if __name__ == "__main__":
    asyncio.run(probe())
