# Multi-Machine Fan-Out

Run discovery in parallel across N machines, then merge.

## Why partition

Sequential discovery on a 30-outlet list with default pacing (`gaussian_sleep` mean 2.5s) takes ~30-60 minutes per outlet × 30 outlets = 15-30 hours. Parallelizing across 3 machines drops wall time to 5-10 hours.

## Partition strategy

Two safe partition strategies. Use **outlet-level** for simplicity.

**Outlet-level (recommended)**: Each machine processes a disjoint subset of outlets.

```bash
# Generate partitions
split -n l/3 outlets.txt outlets_partition_  # creates _aa, _ab, _ac

# Distribute (rsync / git / shared drive / scp):
machine_1: outlets_partition_aa
machine_2: outlets_partition_ab
machine_3: outlets_partition_ac
```

**Journalist-level (advanced)**: One machine runs Step 1 (cheap), then Step 2 fan-outs across N machines on disjoint journalist subsets.

```bash
machine_1: python3 discover_journalists.py outlets.txt --out journalists.jsonl
# distribute journalists.jsonl
split -n l/3 journalists.jsonl journalists_partition_
machine_1: find_articles.py journalists_partition_aa --out articles_aa.jsonl
machine_2: find_articles.py journalists_partition_ab --out articles_ab.jsonl
machine_3: find_articles.py journalists_partition_ac --out articles_ac.jsonl
```

## Per-machine workflow

Each machine runs the standard pipeline against its own partition:

```bash
# === ON MACHINE i ===

# Setup (once)
git clone https://github.com/noique/cross-border-ecommerce-skills
cd cross-border-ecommerce-skills/outbound-prospecting/media-press-discovery
pip install requests beautifulsoup4 dnspython  # add `selenium` if needed for fallback

# Receive your partition
# (e.g. via shared cloud storage or git pull on a scratch branch)
PARTITION=outlets_partition_aa

# Run pipeline against partition
python3 scripts/discover_journalists.py "$PARTITION" --out "journalists_${PARTITION##*_}.jsonl"
python3 scripts/find_articles.py "journalists_${PARTITION##*_}.jsonl" \
    --keywords templates/keywords_template.txt \
    --out "articles_${PARTITION##*_}.jsonl"
python3 scripts/guess_emails.py "journalists_${PARTITION##*_}.jsonl" --out "emails_${PARTITION##*_}.csv"
python3 scripts/score_and_export.py \
    "journalists_${PARTITION##*_}.jsonl" \
    "articles_${PARTITION##*_}.jsonl" \
    "emails_${PARTITION##*_}.csv" \
    --backlinks ~/path/to/kol_prospects.csv \
    --out "pitch_db_${PARTITION##*_}.csv"

# Upload pitch_db_*.csv back to shared location
```

## Merge

On any machine (typically the orchestrator):

```bash
python3 scripts/merge_partitions.py pitch_db_*.csv --out pitch_db_master.csv
```

`merge_partitions.py` deduplicates by `(outlet, journalist)` key, keeps the higher relevance_score on duplicates, and unions the candidate email lists (max 3 unique).

## Avoiding rate limits across machines

Each machine independently paces requests with `gaussian_sleep(mean=2.5, sd=0.7)`. Three machines hitting Muckrack simultaneously = ~3 req/sec aggregate, well under Muckrack's free-tier rate limits (~10 req/sec observed).

If you scale to 5+ machines: stagger machine start times by 2-3 minutes, or implement a Redis-based shared rate-limit token bucket.

## State recovery

Each script reads input files and writes output files. There's no in-memory state. If a machine crashes mid-pipeline:

- Re-run from the last completed step's output. The script will overwrite the in-progress output.
- For Step 1 specifically, you can resume by skipping outlets already present in the JSONL output. (Add `if outlet_slug already in output: continue` if running on a partial file — left as an exercise / future enhancement.)

## Output organization

Recommended folder structure on shared storage:

```
press_discovery_2026-05/
├── input/
│   ├── outlets.txt
│   ├── keywords.txt
│   └── partitions/
│       ├── outlets_partition_aa
│       ├── outlets_partition_ab
│       └── outlets_partition_ac
├── machine_1/
│   ├── journalists_aa.jsonl
│   ├── articles_aa.jsonl
│   ├── emails_aa.csv
│   └── pitch_db_aa.csv
├── machine_2/ ...
├── machine_3/ ...
└── pitch_db_master.csv      ← final merged output
```
