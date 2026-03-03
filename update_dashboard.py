from datetime import datetime
from zoneinfo import ZoneInfo
import pathlib
import re


def update_timestamp_in_html(html_path: str) -> None:
    """
    Update the "Updated: ..." timestamp in index.html to the current time
    in America/Denver.
    """
    path = pathlib.Path(html_path)
    html = path.read_text(encoding="utf-8")

    now_mt = datetime.now(ZoneInfo("America/Denver"))
    formatted = now_mt.strftime("%B %-d, %Y — %I:%M %p MT")

    # Replace the first occurrence after 'Updated:' up to the next closing tag
    pattern = r"Updated:\s*.*?</"
    replacement = f"Updated: {formatted}</"

    new_html, count = re.subn(pattern, replacement, html, count=1, flags=re.DOTALL)

    if count == 0:
        # Insert a new line near the top if we can't find the pattern
        insert = f"Updated: {formatted}\n"
        new_html = insert + html

    path.write_text(new_html, encoding="utf-8")


if __name__ == "__main__":
    update_timestamp_in_html("index.html")
