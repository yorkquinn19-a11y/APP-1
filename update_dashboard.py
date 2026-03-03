from datetime import datetime, timezone
import pathlib


def update_timestamp(html_path="/home/ubuntu/dashboard/index.html"):
    path = pathlib.Path(html_path)
    html = path.read_text(encoding="utf-8")

    now = datetime.now(timezone.utc)
    day = now.day
    formatted = now.strftime("%B ") + str(day) + now.strftime(", %Y — %I:%M %p UTC")

    needle = "Updated:"
    idx = html.find(needle)
    if idx == -1:
        new_html = needle + " " + formatted + "\n" + html
    else:
        lt = html.find("<", idx)
        if lt == -1:
            lt = len(html)
        new_html = html[:idx] + needle + " " + formatted + html[lt:]

    path.write_text(new_html, encoding="utf-8")


if __name__ == "__main__":
    update_timestamp()
