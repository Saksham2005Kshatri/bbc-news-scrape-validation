import csv
import sys
import json
from urllib.parse import urlparse

EXPECTED_COLUMNS = ['title', 'author', 'date', 'image_url', 'article_id', 'link']


def load_csv(filename):
    with open(filename, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return rows


def check_missing_values(rows):
    by_column = {}
    total_missing = 0

    for row_num, row in enumerate(rows, start=1):
        for col in EXPECTED_COLUMNS:
            value = row.get(col, "")
            if not value or value.strip() == "":
                total_missing += 1
                if col not in by_column:
                    by_column[col] = {"count": 0, "rows": []}
                by_column[col]["count"] += 1
                by_column[col]["rows"].append(row_num)

    return {"total_missing": total_missing, "by_column": by_column}


def check_duplicates(rows):
    article_id_map = {}
    link_map = {}

    for row_num, row in enumerate(rows, start=1):
        aid = row.get("article_id", "")
        link = row.get("link", "")

        if aid:
            article_id_map.setdefault(aid, []).append(row_num)
        if link:
            link_map.setdefault(link, []).append(row_num)

    duplicate_article_ids = {
        aid: {"count": len(row_nums), "rows": row_nums}
        for aid, row_nums in article_id_map.items() if len(row_nums) > 1
    }
    duplicate_links = {
        link: {"count": len(row_nums), "rows": row_nums}
        for link, row_nums in link_map.items() if len(row_nums) > 1
    }

    return {
        "duplicate_article_ids": duplicate_article_ids,
        "duplicate_links": duplicate_links,
    }


def is_valid_url(url):
    parsed = urlparse(url)
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


def check_urls(rows):
    invalid_image_urls = []
    invalid_links = []

    for row_num, row in enumerate(rows, start=1):
        image_url = row.get("image_url", "")
        link = row.get("link", "")

        if image_url and not is_valid_url(image_url):
            invalid_image_urls.append({"row": row_num, "value": image_url})
        if link and not is_valid_url(link):
            invalid_links.append({"row": row_num, "value": link})

    return {"image_url": invalid_image_urls, "link": invalid_links}


def validate(filename):
    rows = load_csv(filename)

    missing = check_missing_values(rows)
    duplicates = check_duplicates(rows)
    urls = check_urls(rows)

    report = {
        "summary": {
            "total_rows": len(rows),
            "missing_values_found": missing["total_missing"] > 0,
            "duplicates_found": bool(duplicates["duplicate_article_ids"] or duplicates["duplicate_links"]),
            "invalid_urls_found": bool(urls["image_url"] or urls["link"]),
        },
        "missing_values": missing,
        "duplicates": duplicates,
        "invalid_urls": urls,
    }

    with open("validation_report.json", mode='w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"Validation complete. {len(rows)} rows checked. Report written to validation_report.json")


if __name__ == "__main__":
    filename = sys.argv[1]
    validate(filename)
