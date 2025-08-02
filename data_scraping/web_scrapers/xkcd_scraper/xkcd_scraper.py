import argparse
import os
import sys

import requests

# Python library for pulling data out of HTML and XML files
from bs4 import BeautifulSoup


def get_latest_issue():
    """Get the latest xkcd comic issue number"""
    url = "https://xkcd.com/"
    r = requests.get(url)
    if r.status_code == 200:
        soup = BeautifulSoup(r.content, "html.parser")
        # The permalink typically contains the current comic number
        permalink = soup.find("a", {"rel": "prev"})
        if permalink and permalink.get("href"):  # type: ignore
            # Extract the number from the URL like "/2000/"
            latest = int(permalink.get("href").strip("/")) + 1  # type: ignore
            return latest
    return None


def parse_issue_spec(issue_spec):
    """Parse issue specifications including ranges like '100-105'"""
    if issue_spec.lower() == "latest":
        latest = get_latest_issue()
        return [str(latest)] if latest else []

    if "-" in issue_spec:
        try:
            start, end = map(int, issue_spec.split("-"))
            return [str(i) for i in range(start, end + 1)]
        except ValueError:
            return [issue_spec]  # Return as is if parsing fails

    return [issue_spec]


def scrape_xkcd(issue, save=True):
    meta = {}
    issue = str(issue)
    url = "https://m.xkcd.com/" + issue

    sys.stdout.write("Fetching comic #{}... ".format(issue))
    sys.stdout.flush()
    r = requests.get(url)
    if r.status_code == 200:  # success!
        try:
            soup = BeautifulSoup(r.content, "html.parser")

            img = soup.find("img", {"id": "comic"})
            assert img is not None

            alt_text = img.get("title")  # type: ignore
            img_src = img.get("src")  # type: ignore
            assert isinstance(img_src, str)

            if "http" not in img_src:
                img_src = "https:" + img_src

            title = soup.find("h1", {"id": "title"}).string  # type: ignore

            local_file = None
            if save:
                r_img = requests.get(img_src)
                if r_img.status_code == 200:  # success!
                    extension = os.path.splitext(img_src)[-1]
                    local_file = issue + extension
                    open(local_file, "wb").write(r_img.content)

            meta = {
                "title": title,
                "alt_text": alt_text,
                "img_src": img_src,
                "local_file": local_file,
            }

            sys.stdout.write("done!\n")
        except Exception:
            sys.stdout.write("failed!\n")
    else:
        sys.stdout.write("not found!\n")
    sys.stdout.flush()

    return meta


def main():
    import json

    # Set up argument parser
    parser = argparse.ArgumentParser(description="Scrape comics from xkcd.com")
    parser.add_argument(
        "issues",
        metavar="ISSUE",
        type=str,
        nargs="+",
        help="issue number(s) to scrape. Can be a single issue, a range (e.g., '100-105'), or 'latest'",
    )
    parser.add_argument(
        "-s", "--save", action="store_true", help="save the comic image locally"
    )
    parser.add_argument(
        "-o",
        "--open",
        action="store_true",
        help="open the comic image after downloading",
    )

    # Parse arguments
    args = parser.parse_args()

    # Process all issue specifications
    all_issues = []
    for issue_spec in args.issues:
        all_issues.extend(parse_issue_spec(issue_spec))

    for issue in all_issues:
        meta = scrape_xkcd(issue, args.save)
        print(json.dumps(meta, indent=2))

        if args.open and meta.get("local_file"):
            try:
                os.system(f"eog {meta['local_file']}")
            except Exception:
                pass


if __name__ == "__main__":
    main()
