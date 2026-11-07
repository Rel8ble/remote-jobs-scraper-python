# Remote jobs scraper and API in Python: Remote OK, We Work Remotely, Remotive, Himalayas, Jobicy

Pull live remote jobs from seven boards (Remote OK, We Work Remotely, Remotive, Himalayas, Jobicy, Working Nomads, Arbeitnow) into one list from Python, with salaries parsed into numbers, then turn them into a small salary and hiring-signal report.

> I built this actor; it's a paid tool on Apify: [Remote Jobs Scraper & Aggregator](https://apify.com/rel8ble/remote-jobs-aggregator). $0.25 per 1,000 jobs, no start fee.

## What you get per job

Title, company, board name and original job URL, apply link, who can apply (countries / regions / worldwide), employment type, seniority, category, tags, salary as text and as min / max / currency / period plus an approximate yearly USD figure, posted date, and the other boards listing the same job (duplicates across boards are merged). The full description is optional.

## Quick start (Python)

```bash
pip install -r requirements.txt
export APIFY_TOKEN=<YOUR_APIFY_TOKEN>
python example.py --location USA --min-salary 100000 --full-time
```

The core call:

```python
from apify_client import ApifyClient

client = ApifyClient("<YOUR_APIFY_TOKEN>")
run = client.actor("rel8ble/remote-jobs-aggregator").call(run_input={
    "keywords": ["python", "data engineer"],
    "locations": ["Europe"],
    "postedWithinDays": 7,
    "maxItems": 200,
    "includeDescription": False,
})
for job in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(job["title"], "|", job["company"], "|", job["sourceName"], "|", job.get("salaryText"))
```

## Node.js

```js
import { ApifyClient } from 'apify-client';

const client = new ApifyClient({ token: '<YOUR_APIFY_TOKEN>' });
const run = await client.actor('rel8ble/remote-jobs-aggregator').call({
  locations: ['USA'], minSalary: 100000, maxItems: 100, includeDescription: false,
});
const { items } = await client.dataset(run.defaultDatasetId).listItems();
console.log(items.length, items[0]?.title);
```

## Main input fields

| field | example | meaning |
|---|---|---|
| `sources` | `["remoteok","himalayas"]` | boards to read; default all seven |
| `keywords` / `excludeKeywords` | `["react"]` / `["senior"]` | match title, company, category or tags |
| `locations` | `["USA"]`, `["Europe"]` | who can apply; worldwide jobs kept unless `includeWorldwide: false` |
| `minSalary` | `100000` | top of range at least this, USD per year |
| `employmentTypes` | `["Full-time"]` | Full-time, Part-time, Contract, Freelance ... |
| `postedWithinDays` | `1` | only fresh jobs |
| `maxItems` | `100` | cap; boards get a fair share when it cuts |

## Real output

`sample-output.json` holds 100 real rows (description left out) from a local run on 16 Oct 2026 with `locations: ["USA"]`, `minSalary: 100000`, `employmentTypes: ["Full-time"]`. One row, trimmed:

```json
{
  "sourceName": "Remotive",
  "title": "Tech Lead Full-Stack Rails Engineer",
  "company": "Mitre Media",
  "location": "USA, Canada, USA timezones",
  "employmentType": "Full-time",
  "category": "Software Development",
  "salaryText": "$170k - $200k",
  "salaryYearlyUsdMin": 170000,
  "salaryYearlyUsdMax": 200000,
  "postedAt": "2026-10-14T20:33:44.000Z"
}
```

`python example.py --from-json sample-output.json` on that file (no Apify call) prints, among other things:

```
Jobs per board:
  Himalayas          50
  Jobicy             49
  Remotive           1

Median top-of-range pay by category (3+ jobs):
  Sales                           29 jobs   median $120k - $175k
  Product & Operations             6 jobs   median $143k - $192k
  Data Science                     5 jobs   median $130k - $175k
  Developer                        5 jobs   median $160k - $245k
  Cybersecurity                    3 jobs   median $200k - $230k

Best-paid openings:
  $330k-$543k  Enterprise Sales Leader - Technology and Telecommunications @ Qualtrics (Jobicy)
  $260k-$340k  SVP, Partners @ Vonage (Jobicy)
  $208k-$312k  Security Software Engineer, IAM @ Vercel (Jobicy)
```

Sales was the biggest group of US remote jobs paying $100k+ in that snapshot (29 of 100). Small groups are only a few jobs each, so treat their medians as a hint, not a benchmark. Every row in this sample has a salary because a `minSalary` filter drops unpaid listings unless you set `includeNoSalary: true`.

## Pricing

$0.25 per 1,000 jobs, no start fee, no extra charge for descriptions, deduplication or filters. 100 jobs = $0.025. Apify's free plan credit covers small tests.

## Limits

- Reads the public feeds the boards publish for re-use, so it sees what those feeds carry, not each board's full archive: Remotive's free feed is a small set (about 15 jobs, 24 hours late), Remote OK and Working Nomads publish only their newest ~100 and ~50 jobs.
- Remote OK leaves eligibility empty on many jobs and sometimes gives only a city; the `locations` filter can't place those (see `includeUnknownLocation`).
- Yearly USD salary is approximate for hourly, daily or non-USD pay.
- Boards ask to be credited: every row keeps `sourceName` and the original `sourceUrl`; keep the link if you republish.

## Related

- [ATS job boards scraper (Greenhouse, Lever, Ashby, Workday)](https://github.com/Rel8ble/greenhouse-lever-ashby-jobs-scraper-python)
- [SEEK jobs scraper](https://github.com/Rel8ble/seek-jobs-scraper-python)
- [JobStreet / JobsDB scraper](https://github.com/Rel8ble/jobstreet-jobsdb-scraper-python)

Need a custom scraper or a ready dataset? Hire me on Fiverr: https://www.fiverr.com/rel8ble

MIT licensed example code.
