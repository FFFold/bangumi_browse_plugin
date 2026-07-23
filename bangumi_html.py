"""Bangumi HTML 页面解析器。"""

from __future__ import annotations

import re

import httpx
from bs4 import BeautifulSoup, Tag

from .models import CalendarDay, CalendarItem, EpisodeComment, ReviewDetail, ReviewSummary


BGM_BASE = "https://bgm.tv"


class BangumiHTMLError(Exception):
    pass


async def _fetch(client: httpx.AsyncClient, url: str, timeout: int) -> str:
    try:
        resp = await client.get(url, timeout=timeout, follow_redirects=True)
        resp.raise_for_status()
    except httpx.TimeoutException:
        raise BangumiHTMLError("请求 Bangumi 页面超时，请稍后重试")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise BangumiHTMLError("未找到该页面，请检查 ID 是否正确")
        raise BangumiHTMLError(f"请求 Bangumi 页面失败 (HTTP {e.response.status_code})")
    except httpx.RequestError as e:
        raise BangumiHTMLError(f"请求 Bangumi 页面失败: {e}")
    return resp.text


_WEEKDAY_EN2CN = {
    "Sun": "周日",
    "Mon": "周一",
    "Tue": "周二",
    "Wed": "周三",
    "Thu": "周四",
    "Fri": "周五",
    "Sat": "周六",
}


async def fetch_calendar(
    client: httpx.AsyncClient,
    timeout: int = 15,
) -> list[CalendarDay]:
    """获取本周每日放送表。"""
    html = await _fetch(client, f"{BGM_BASE}/calendar", timeout)
    soup = BeautifulSoup(html, "lxml")

    days: list[CalendarDay] = []
    week_items = soup.select(".BgmCalendar ul.large > li.week")

    for week_li in week_items:
        dt = week_li.select_one("dt")
        dd = week_li.select_one("dd")

        if not dt or not dd:
            continue

        dt_class = dt.get("class", [])
        en_day = (dt_class[0] if isinstance(dt_class, list) and dt_class else "Sun")
        if isinstance(en_day, str):
            en_day = en_day.split()[0] if en_day else "Sun"

        cn_day = _WEEKDAY_EN2CN.get(en_day, en_day)

        day = CalendarDay(weekday=cn_day, date="", items=[])

        header = dt.select_one("h3")
        if header:
            day.date = header.get_text(strip=True)

        item_els = dd.select("ul.coverList > li")
        for item_el in item_els:
            link = item_el.select_one("a.nav")
            if not link:
                continue

            href = link.get("href", "")
            subject_id = 0
            m = re.search(r"/subject/(\d+)", str(href))
            if m:
                subject_id = int(m.group(1))

            name_cn = link.get_text(strip=True)

            orig_el = item_el.select_one("small em")
            name = orig_el.get_text(strip=True) if orig_el else ""

            day.items.append(CalendarItem(
                subject_id=subject_id,
                name=name,
                name_cn=name_cn,
                time="",
                cover="",
            ))

        days.append(day)

    return days


async def fetch_episode_comments(
    client: httpx.AsyncClient,
    episode_id: int,
    limit: int = 20,
    timeout: int = 15,
) -> list[EpisodeComment]:
    """获取单集吐槽箱评论。

    Bangumi 通过 JavaScript 动态加载评论，HTML 中 #comment_list 为空。
    如果无法获取，返回空列表并提示用户。
    """
    html = await _fetch(client, f"{BGM_BASE}/ep/{episode_id}", timeout)
    soup = BeautifulSoup(html, "lxml")

    # 尝试从页面提取可能的嵌入式评论数据
    comment_list = soup.select_one("#comment_list")
    if not comment_list:
        return []

    replies = comment_list.select(".row_reply, .reply_item, div.reply")
    if not replies:
        return []

    comments: list[EpisodeComment] = []
    for reply in replies[:limit]:
        user_el = reply.select_one("a.avatar, a.l, span.user")
        username = ""
        if user_el:
            username = user_el.get("title", "") or user_el.get_text(strip=True)

        content_el = reply.select_one(".reply_content, .message, .text, .content")
        content = content_el.get_text("\n", strip=True) if content_el else ""

        time_el = reply.select_one("small.greytext, .time, .date, span.tip")
        time_str = time_el.get_text(strip=True) if time_el else ""

        comments.append(EpisodeComment(
            username=username,
            score="",
            content=content,
            time=time_str,
        ))

    return comments


async def fetch_reviews_list(
    client: httpx.AsyncClient,
    subject_id: int,
    limit: int = 10,
    timeout: int = 15,
) -> list[ReviewSummary]:
    """获取作品长评列表。"""
    html = await _fetch(client, f"{BGM_BASE}/subject/{subject_id}/reviews", timeout)
    soup = BeautifulSoup(html, "lxml")

    items = soup.select("#entry_list .item.clearit")
    reviews: list[ReviewSummary] = []

    for item in items[:limit]:
        title_el = item.select_one("h2.title a.l")
        href = title_el.get("href", "") if title_el else ""
        review_id = 0
        m = re.search(r"/blog/(\d+)", href)
        if m:
            review_id = int(m.group(1))

        title = title_el.get_text(strip=True) if title_el else ""

        author_el = item.select_one("a.avatar")
        author = author_el.get("title", "") if author_el else ""

        content_el = item.select_one("div.content a, div.summary")
        summary = content_el.get_text(strip=True) if content_el else ""

        time_el = item.select_one("small.greytext, .time, .date")
        time_str = time_el.get_text(strip=True) if time_el else ""

        reviews.append(ReviewSummary(
            review_id=review_id,
            title=title,
            author=author,
            time=time_str,
            score=0,
            summary=summary,
        ))

    return reviews


async def fetch_review_detail(
    client: httpx.AsyncClient,
    review_id: int,
    timeout: int = 15,
) -> ReviewDetail:
    """获取单篇长评完整内容。"""
    html = await _fetch(client, f"{BGM_BASE}/blog/{review_id}", timeout)
    soup = BeautifulSoup(html, "lxml")

    title_el = soup.select_one("h1")
    title = title_el.get_text(strip=True) if title_el else ""

    author_el = soup.select_one(".author, a.avatar")
    author = ""
    if author_el:
        author = author_el.get("title", "") or author_el.get_text(strip=True)

    time_el = soup.select_one(".time, .date, small.greytext")
    time_str = time_el.get_text(strip=True) if time_el else ""

    content_el = soup.select_one(".content, .entry, article")
    content = content_el.get_text("\n", strip=True) if content_el else ""

    return ReviewDetail(
        review_id=review_id,
        title=title,
        author=author,
        time=time_str,
        score=0,
        content=content,
    )
