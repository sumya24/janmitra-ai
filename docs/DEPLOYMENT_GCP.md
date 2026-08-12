# Deployment — Google Cloud (stopgap while Oracle signup is blocked)

> **This is a stopgap, not the intended long-term home.** `docs/DEPLOYMENT.md` (Oracle Cloud) is
> still the better fit long-term — genuinely free forever, vs. either a tiny free VM or a 90-day
> credit window here. Plan to migrate later (the Docker setup doesn't change — same containers,
> just pointed at a different VM). Everything in `docs/DEPLOYMENT.md`'s "What all these files
> actually are", "How CI/CD works day to day", "Rollback", and most of "Operating notes"
> sections applies here unchanged — this doc only covers what's different about GCP.

## Your account status

You already created the GCP account and clicked "upgrade to full account" — so this is a **paid
billing account with $300 (~₹28,694) trial credit**, expiring **11 November 2026**. That's fine
— upgrading itself isn't a mistake, it just means billing is *live* instead of impossible, so
you need a plan for when the credit runs out rather than assuming nothing happens. Because of
this, you actually have **two real options**, not one:

| | Option A — Free `e2-micro` | Option B — Paid `e2-medium` (uses your credit) |
|---|---|---|
| Cost | $0, forever | ~$25-30/month, paid from your existing $300 credit |
| RAM | 1GB — needs a swap file, expect real slowdowns | 4GB — comfortable real headroom, no swap needed |
| Region | US only (Oregon/Iowa/South Carolina) — no India region on the free tier | **Mumbai** (`asia-south1`) — real latency to your users |
| Time limit | None | Until the credit runs out (~11 Nov 2026), or you decide to keep paying |
| Best for | Long-term $0 hosting once you've decided this is where the app stays | Right now, while you're still deciding — the credit is sitting there either way |

**My take:** go with **Option B** right now. That $300 credit expires in ~90 days no matter what
you do with it — running a properly-sized VM for those 90 days costs a small fraction of it and
gives you an app that actually performs well, instead of deliberately crippling it on Option A
while unused credit sits on the table. The decision that actually matters — free forever vs.
paying vs. migrating to Oracle — is one you make *at* the 90-day mark, not now.

### Why Option A's 1GB is actually tight (not just "a bit less")

This backend loads several things into memory at once, and `backend/main.py`'s startup
deliberately warms the embedding model eagerly (so the first real request isn't slow) — meaning
this is memory the app claims immediately on boot, not just under peak load:

| Component | Approx. RAM |
|---|---|
| Python + FastAPI + uvicorn baseline | ~100MB |
| torch (just importing it) | ~200-300MB |
| sentence-transformers model (multilingual-e5-small), loaded | ~500-700MB |
| ChromaDB | ~100-200MB |
| LangGraph/LangChain orchestration | ~50-100MB |
| **Backend total, just sitting idle** | **~950MB-1.4GB** |

That's before the OS, Docker itself, and the Caddy container (which also has to fit on the same
1GB VM) take their share. So on Option A, a swap file isn't a "nice to have" — without it, expect
the backend to get OOM-killed at startup or on the first Ask JanMitra request. Swap doesn't add
real memory either; it lets the OS spill overflow onto disk instead of crashing, which is roughly
100-1000x slower than RAM — it turns "crashes" into "works, but noticeably slower," not into
"works properly." Option B's 4GB avoids all of this outright.

## Step 0 (do this first, whichever option you pick): budget alert + a calendar reminder

1. In the Console: **Billing → Budgets & alerts → Create budget**. Set it to something like
   ₹5,000 (well under your ₹28,694) so you get an email if usage spikes unexpectedly. Note this
   only *alerts* you — it doesn't stop anything automatically.
2. **Set an actual calendar reminder for ~1 November 2026** (10 days before the credit expires)
   to act on the "Before the credit runs out" section below. This matters more than the budget
   alert — an alert you ignore doesn't stop a bill.

## One-time setup

### 1. Create the VM (Console walkthrough)

Go to [console.cloud.google.com](https://console.cloud.google.com), make sure the right project
is selected in the top bar (the `project-0977686d-...` one from your screenshot), then:

1. **Left-side hamburger menu (☰) → Compute Engine → VM instances.** First time opening
   Compute Engine on a project takes ~30-60 seconds to "enable the API" — just wait, it's normal.
2. Click **Create Instance** (top of the page).
3. **Name**: `janmitra-vm` (or anything — this is just a label).
4. **Region** and **Zone** — pick based on your option:
   - **Option B (recommended)**: Region = `asia-south1 (Mumbai)`, Zone = `asia-south1-a`.
   - **Option A (free)**: Region = `us-central1 (Iowa)` (or `us-west1`/`us-east1`), Zone = any
     `-a`/`-b`/`-c` under it. Must be one of these three regions or it won't be Always Free.
5. **Machine configuration** — scroll to the machine type section:
   - **Option B**: family "E2", machine type `e2-medium` (2 vCPU, 4GB memory).
   - **Option A**: family "E2", machine type `e2-micro` (2 vCPU shared-core, 1GB memory).
6. **Boot disk** — click **Change** (it defaults to Debian, you want Ubuntu):
   - Operating system: **Ubuntu**
   - Version: **Ubuntu 24.04 LTS**
   - Boot disk type: Standard persistent disk (leave default)
   - Size: **30** GB
   - Click **Select** to confirm and close that panel.
7. **Firewall** section (further down the same page): check both
   **"Allow HTTP traffic"** and **"Allow HTTPS traffic"**. This is the *only* firewall step
   needed on GCP — no separate `iptables` step on the VM itself like Oracle requires.
8. Everything else: leave as default.
9. Click **Create** at the bottom. It takes maybe 30-60 seconds to boot; you'll land back on the
   VM instances list and see it appear with a green checkmark once it's running, along with its
   **External IP** — note that IP down, you'll need it for the domain and GitHub secrets steps
   later.
10. To SSH in: click the **SSH** button directly in that instance's row in the console — it
    opens a browser-based terminal and handles your SSH key for you automatically, no key setup
    needed on your end.

If you'd rather use the `gcloud` CLI instead of clicking through the Console, here's the
equivalent (only if you already have `gcloud` installed and authenticated):

```bash
# Option B -- e2-medium in Mumbai
gcloud compute instances create janmitra-vm \
  --zone=asia-south1-a \
  --machine-type=e2-medium \
  --image-family=ubuntu-2404-lts-amd64 \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=30GB \
  --tags=http-server,https-server

# Option A -- free e2-micro (pick one region: us-west1, us-central1, or us-east1)
gcloud compute instances create janmitra-vm \
  --zone=us-central1-a \
  --machine-type=e2-micro \
  --image-family=ubuntu-2404-lts-amd64 \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=30GB \
  --tags=http-server,https-server

# Either way, also run this once (same firewall rule for both options)
gcloud compute firewall-rules create allow-http-https \
  --allow=tcp:80,tcp:443 --target-tags=http-server,https-server
```

### 2. Install Docker

SSH into the VM (Console's "SSH" button, or `gcloud compute ssh janmitra-vm --zone=<your-zone>`):

```bash
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
newgrp docker
docker compose version   # confirm the Compose plugin is present
```

**Option A only** — also add swap, or the backend will very likely get OOM-killed on startup or
on the first Ask JanMitra request (1GB isn't enough on its own for torch + sentence-transformers
+ ChromaDB together):

```bash
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab   # persists across reboots
free -h   # confirm swap shows up
```

**Option B** doesn't need this — 4GB is real headroom for this stack.

### 3. Clone the repo and set up secrets

Identical to Oracle's setup — see `docs/DEPLOYMENT.md` step 3. Same `.env.example` → `.env`
copy, same variables.

### 4. First deploy

Identical commands either way:

```bash
docker compose -f docker-compose.prod.yml up -d --build
curl http://localhost/health
```

**Option A only**: watch memory while it starts (`docker stats` in another SSH session) — if the
backend container restarts repeatedly right after boot, that's the OOM killer; confirm swap is
actually active (`free -h` should show a non-zero Swap line) before troubleshooting further.

### 5. Set up automated deployment (GitHub Actions CD)

This wires up `.github/workflows/cd.yml` so every merge to `main` automatically deploys to this
VM, instead of you SSHing in and running `docker compose` by hand each time.

**a) Generate a dedicated deploy keypair** (on your own laptop, not the VM — this key's private
half becomes a GitHub secret, its public half goes on the VM):

```bash
ssh-keygen -t ed25519 -f ~/.ssh/janmitra_deploy_key -N "" -C "github-actions-deploy"
```

Don't reuse your personal SSH key here — a dedicated key means you can revoke deploy access
later (by removing it from the VM's `authorized_keys`) without touching your own login.

**b) Add the public half to the VM.** SSH into the VM (Console's SSH button) and run:

```bash
echo "<paste the contents of ~/.ssh/janmitra_deploy_key.pub here>" >> ~/.ssh/authorized_keys
```

**c) Make sure the VM has a real, up-to-date clone with secrets configured.** If you cloned the
repo earlier (before this work was pushed to `main`), re-clone it — the old clone predates all of
this and won't have the current Dockerfiles/compose file:

```bash
cd ~
rm -rf janmitra-ai   # only if you have an old/stale clone from before -- skip if this is your first clone
git clone https://github.com/<your-username>/janmitra-ai.git
cd janmitra-ai
cp .env.example .env
nano .env   # fill in SARVAM_API_KEY, and set JWT_SECRET_KEY to a fixed value: openssl rand -hex 32
```

**d) Get the VM's external IP** — either from the Console (Compute Engine → VM instances →
External IP column), or by running this on the VM:

```bash
curl -s ifconfig.me
```

**e) Add the 5 GitHub secrets.** Either via the GitHub web UI (**repo → Settings → Secrets and
variables → Actions → New repository secret**), or with the `gh` CLI from your laptop if you have
it installed and authenticated:

```bash
gh secret set SSH_HOST --body "<the VM's external IP from step d>"
gh secret set SSH_USER --body "<your VM username -- the part before @ in your SSH prompt, e.g. gpkp182093>"
gh secret set SSH_PRIVATE_KEY < ~/.ssh/janmitra_deploy_key
gh secret set SSH_DEPLOY_PATH --body "/home/<your VM username>/janmitra-ai"
```

`SSH_PORT` is optional — the workflow defaults to `22` if you don't set it.

**f) Verify it actually works.** The easiest way: make any small commit to `main` (even just this
doc) and push — that re-triggers CI, and once CI passes, CD fires automatically. Watch it with:

```bash
gh run list --workflow=cd.yml --limit 1
gh run watch   # follow the most recent run live
```

If the SSH step fails, double check: the public key is really in the VM's `~/.ssh/authorized_keys`
(one line, no extra whitespace), `SSH_DEPLOY_PATH` matches exactly where you cloned the repo, and
`SSH_USER` matches your actual VM login username (not your Google account email).

### 6. Domain/HTTPS (optional)

Identical to Oracle's step 5 in `docs/DEPLOYMENT.md` — set `SITE_ADDRESS=your-domain.com` in the
VM's `.env` once a domain points at its IP, then `docker compose -f docker-compose.prod.yml up -d`
to pick up the change. Caddy handles the Let's Encrypt certificate automatically from there.

## Before the credit runs out (~1 November 2026) — only matters if you picked Option B

Pick one, don't let it default to "do nothing":

- **Migrate to Oracle** (or wherever else you've landed by then) — see the migration section
  below.
- **Downsize to a free `e2-micro`** in one of the three Always Free regions (not Mumbai, that's
  not Always Free) — this is just switching to Option A above, genuinely $0 but tighter and
  worse latency.
- **Keep paying deliberately** for `e2-medium` in Mumbai (~$25-30/month) if the project's at a
  point where that's worth it.

Whatever you pick, do it *before* 11 November, not after — that's the date billing stops being
covered by credit and starts being covered by your card.

## Migrating to Oracle (or anywhere else) later

Nothing about the app or its containers is GCP-specific. To move: stand up the new VM per
`docs/DEPLOYMENT.md`, restore the `backend_state` volume's contents (the backup command in that
doc's "Operating notes" section) onto it, point the domain's DNS at the new IP, and update the
`SSH_HOST`/`SSH_DEPLOY_PATH` GitHub secrets. No code or Docker config changes needed either way.
