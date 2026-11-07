"""Remote jobs salary report: pull remote jobs from Remote OK, We Work Remotely,
Remotive, Himalayas, Jobicy, Working Nomads and Arbeitnow through the
rel8ble/remote-jobs-aggregator actor on Apify, save them to CSV and print
pay by category, the companies hiring the most, and the best-paid openings.

  python example.py --location USA --min-salary 100000
  python example.py --keyword python --keyword "data engineer" --location Europe --days 7
  python example.py --from-json sample-output.json      # offline, no Apify call
"""
import argparse
import csv
import json
import os
import statistics
from collections import Counter, defaultdict

COLUMNS = [
    "title", "company", "sourceName", "location", "employmentType", "category",
    "salaryYearlyUsdMin", "salaryYearlyUsdMax", "salaryText", "postedAt", "applyUrl",
]


def fetch(args):
    from apify_client import ApifyClient

    token = os.environ.get("APIFY_TOKEN") or "<YOUR_APIFY_TOKEN>"
    run_input = {"maxItems": args.max_items, "includeDescription": False}
    if args.keyword:
        run_input["keywords"] = args.keyword
    if args.location:
        run_input["locations"] = args.location
    if args.min_salary:
        run_input["minSalary"] = args.min_salary
    if args.days:
        run_input["postedWithinDays"] = args.days
    if args.full_time:
        run_input["employmentTypes"] = ["Full-time"]

    client = ApifyClient(token)
    run = client.actor("rel8ble/remote-jobs-aggregator").call(run_input=run_input)
    return list(client.dataset(run["defaultDatasetId"]).iterate_items())


def usd(n):
    return f"${n / 1000:,.0f}k" if n else "-"


def report(jobs, out_path):
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
        w.writeheader()
        for j in jobs:
            w.writerow(j)
    print(f"{len(jobs)} jobs saved to {out_path}")

    print("\nJobs per board:")
    for board, n in Counter(j.get("sourceName") for j in jobs).most_common():
        print(f"  {board:<18} {n}")

    paid = [j for j in jobs if j.get("salaryYearlyUsdMax")]
    print(f"\n{len(paid)} of {len(jobs)} publish a salary.")
    by_cat = defaultdict(list)
    for j in paid:
        by_cat[j.get("category") or "(no category)"].append(j)
    print("\nMedian top-of-range pay by category (3+ jobs):")
    for cat, rows in sorted(by_cat.items(), key=lambda kv: -len(kv[1])):
        if len(rows) < 3:
            continue
        lows = [r["salaryYearlyUsdMin"] for r in rows if r.get("salaryYearlyUsdMin")]
        highs = [r["salaryYearlyUsdMax"] for r in rows]
        low = statistics.median(lows) if lows else None
        print(f"  {cat:<30} {len(rows):>3} jobs   median {usd(low)} - {usd(statistics.median(highs))}")

    print("\nCompanies with the most openings (hiring signal):")
    for company, n in Counter(j.get("company") for j in jobs).most_common(8):
        if n < 2:
            break
        print(f"  {company:<32} {n}")

    print("\nBest-paid openings:")
    top = sorted(paid, key=lambda j: j["salaryYearlyUsdMax"], reverse=True)[:5]
    for j in top:
        print(f"  {usd(j.get('salaryYearlyUsdMin'))}-{usd(j['salaryYearlyUsdMax'])}  "
              f"{j['title']} @ {j['company']} ({j.get('sourceName')})")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--keyword", action="append", help="keyword, repeatable")
    p.add_argument("--location", action="append", help="who can apply: USA, Europe, UK, Worldwide ...")
    p.add_argument("--min-salary", type=int, help="top of range at least this, USD per year")
    p.add_argument("--days", type=int, help="posted within the last N days")
    p.add_argument("--full-time", action="store_true")
    p.add_argument("--max-items", type=int, default=200)
    p.add_argument("--from-json", help="read a saved dataset instead of calling Apify")
    p.add_argument("--out", default="remote_jobs.csv")
    args = p.parse_args()

    if args.from_json:
        with open(args.from_json, encoding="utf-8") as f:
            jobs = json.load(f)
    else:
        jobs = fetch(args)
    report(jobs, args.out)


if __name__ == "__main__":
    main()
