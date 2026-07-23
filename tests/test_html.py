"""HTML 解析器集成测试。"""
import asyncio
import sys
import io

import httpx

from bangumi_browse_plugin.bangumi_html import (
    fetch_calendar,
    fetch_reviews_list,
    fetch_review_detail,
)


async def test():
    async with httpx.AsyncClient(
        proxy="http://127.0.0.1:7897",
        headers={"User-Agent": "Fold/bangumi-test"},
        timeout=20,
        follow_redirects=True,
    ) as c:
        # Test 1: Calendar
        print("=== Calendar ===")
        days = await fetch_calendar(c, timeout=15)
        print(f"  Got {len(days)} days")
        for day in days:
            print(f"  {day.weekday}: {len(day.items)} items")
            for item in day.items[:2]:
                print(f"    [{item.subject_id}] {item.name_cn or item.name}")
        print("  PASS\n")

        # Test 2: Reviews list
        print("=== Reviews List ===")
        reviews = await fetch_reviews_list(c, 237, limit=3, timeout=15)
        print(f"  Got {len(reviews)} reviews")
        for r in reviews:
            print(f"    [{r.review_id}] {r.title[:60]} by {r.author[:20]}")
            if r.summary:
                print(f"      summary: {r.summary[:80]}...")
        print("  PASS\n")

        # Test 3: Review detail
        if reviews:
            print("=== Review Detail ===")
            review = await fetch_review_detail(c, reviews[0].review_id, timeout=15)
            print(f"  Title: {review.title[:80]}")
            print(f"  Author: {review.author[:30]}")
            print(f"  Content length: {len(review.content)} chars")
            print(f"  Content preview: {review.content[:200]}...")
            print("  PASS\n")

        print("ALL HTML TESTS PASSED!")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    asyncio.run(test())
