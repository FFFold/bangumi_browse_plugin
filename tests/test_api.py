"""Bangumi API 客户端集成测试。"""
import asyncio

import httpx

from bangumi_browse_plugin.bangumi_api import BangumiAPI


async def test():
    async with httpx.AsyncClient(
        proxy="http://127.0.0.1:7897",
        headers={"User-Agent": "Fold/bangumi-test"},
    ) as c:
        api = BangumiAPI(c, timeout=15)

        # Test 1: Search
        print("=== 搜索测试 ===")
        subjects = await api.search_subjects("攻壳机动队", limit=3)
        for s in subjects:
            score = s.rating.score if s.rating else "N/A"
            print(f"  [{s.id}] {s.name_cn or s.name} ({s.type}) 评分: {score}")
        print("  PASS\n")

        # Test 2: Subject detail
        print("=== 条目详情测试 ===")
        detail = await api.get_subject(subjects[0].id)
        print(f"  {detail.name_cn} | 放送: {detail.date} | 集数: {detail.eps} | 排名: #{detail.rank}")
        print("  PASS\n")

        # Test 3: Persons
        print("=== 制作人员测试 ===")
        persons = await api.get_subject_persons(subjects[0].id)
        print(f"  {len(persons)} 人:")
        for p in persons[:5]:
            print(f"    {p.relation}: {p.name}")
        print("  PASS\n")

        # Test 4: Episodes (use anime subject 237)
        print("=== 剧集列表测试 ===")
        anime_id = 237  # 攻壳机动队 TV
        episodes = await api.get_episodes(anime_id, limit=3)
        for ep in episodes:
            print(f"  EP{ep.ep} {ep.name_cn or ep.name} ({ep.comment}条评论)")
        print("  PASS\n")

        # Test 5: Season browse
        print("=== 季度浏览测试 ===")
        season = await api.browse_subjects("anime", year=2026, month=7, limit=3)
        for s in season:
            print(f"  [{s.id}] {s.name_cn or s.name}")
        print("  PASS\n")

        # Test 6: Relations
        print("=== 关联作品测试 ===")
        rels = await api.get_subject_relations(subjects[0].id)
        print(f"  {len(rels)} 个关联:")
        for r in rels:
            print(f"    {r.relation}: {r.name_cn or r.name}")
        print("  PASS\n")

        print("ALL API TESTS PASSED!")


if __name__ == "__main__":
    asyncio.run(test())
