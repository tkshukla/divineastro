# Divine Astro — create the production VM on GCP and deploy.
#
#   .\deploy\provision.ps1              create the VM and deploy
#   .\deploy\provision.ps1 -Redeploy    push code changes to an existing VM
#
# The VM sits in asia-south1 (Mumbai) — lowest latency for Indian users, and
# keeps customer data in-country, which is the sensible default under the DPDP
# Act even though it is not strictly required.

param(
    [string]$Project  = "astro-505710",
    [string]$Zone     = "asia-south1-a",
    [string]$Name     = "divineastro",
    [string]$Machine  = "e2-small",
    [switch]$Redeploy
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)

function Step($msg) { Write-Host "`n=== $msg ===" -ForegroundColor Cyan }

# gcloud's ssh/scp to this VM drops with "Connection reset by peer" often enough
# that a one-shot deploy fails several times an evening. Retrying is safe: every
# remote step here is idempotent, and the caller still throws if all tries fail.
function Retry-Remote {
    param([scriptblock]$Action, [string]$What, [int]$Tries = 4)
    for ($i = 1; $i -le $Tries; $i++) {
        & $Action
        if ($LASTEXITCODE -eq 0) { return }
        if ($i -lt $Tries) {
            Write-Host "  $What failed (attempt $i/$Tries) — retrying in $($i * 8)s" -ForegroundColor DarkYellow
            Start-Sleep -Seconds ($i * 8)
        }
    }
    throw "$What failed after $Tries attempts. The running site is untouched."
}

gcloud config set project $Project | Out-Null

if (-not $Redeploy) {
    Step "Enabling APIs"
    gcloud services enable compute.googleapis.com --project $Project

    Step "Reserving a static IP"
    $existing = gcloud compute addresses list --filter="name=$Name-ip" --format="value(name)" --project $Project
    if (-not $existing) {
        gcloud compute addresses create "$Name-ip" --region ($Zone -replace '-[a-z]$','') --project $Project
    }
    $ip = gcloud compute addresses describe "$Name-ip" --region ($Zone -replace '-[a-z]$','') --format="value(address)" --project $Project
    Write-Host "  static IP: $ip" -ForegroundColor Green

    Step "Firewall — HTTP/HTTPS only"
    foreach ($rule in @(@{n="allow-http"; p="tcp:80"}, @{n="allow-https"; p="tcp:443"})) {
        $have = gcloud compute firewall-rules list --filter="name=$($rule.n)" --format="value(name)" --project $Project
        if (-not $have) {
            gcloud compute firewall-rules create $rule.n --allow=$($rule.p) `
                --target-tags=https-server --description="Divine Astro" --project $Project
        }
    }

    Step "Creating the VM ($Machine, $Zone)"
    gcloud compute instances create $Name `
        --project $Project --zone $Zone --machine-type $Machine `
        --image-family=debian-12 --image-project=debian-cloud `
        --boot-disk-size=30GB --boot-disk-type=pd-balanced `
        --address $ip --tags=https-server `
        --metadata=enable-oslogin=TRUE `
        --scopes=https://www.googleapis.com/auth/cloud-platform

    Step "Installing Docker on the VM"
    # e2-small has 2 GB of RAM. Compiling pyswisseph and timezonefinder, and
    # running Postgres alongside the app, will exceed that at peak — the build
    # gets OOM-killed with a confusing error. 4 GB of swap absorbs the spikes;
    # steady-state usage stays in RAM so the disk is not in the hot path.
    $install = @'
set -e
if [ ! -f /swapfile ]; then
  sudo fallocate -l 4G /swapfile
  sudo chmod 600 /swapfile
  sudo mkswap /swapfile
  sudo swapon /swapfile
  echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab > /dev/null
  # Prefer RAM; only reach for swap under real pressure.
  echo 'vm.swappiness=10' | sudo tee /etc/sysctl.d/99-swap.conf > /dev/null
  sudo sysctl -p /etc/sysctl.d/99-swap.conf
  echo "swap enabled"
fi
sudo apt-get update -qq
sudo apt-get install -y -qq ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian $(. /etc/os-release && echo $VERSION_CODENAME) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update -qq
sudo apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER
sudo mkdir -p /opt/divineastro && sudo chown $USER /opt/divineastro
echo "docker ready"
'@
    ($install -replace "`r", "") | gcloud compute ssh $Name --zone $Zone --project $Project --command "bash -s"
}

Step "Uploading the application"
# Everything except secrets, local state and the venv. .env is sent separately
# so it is never part of a bulk copy that might be logged.
# Note the /XF patterns: `.env*` catches .env.production and .env.example too
# (the production values are uploaded separately, below, straight to .env), and
# client_secret*.json keeps the downloaded Google OAuth file off the server.
$staging = Join-Path $env:TEMP "divineastro-deploy"
if (Test-Path $staging) { Remove-Item $staging -Recurse -Force }
New-Item -ItemType Directory -Path $staging | Out-Null
robocopy $root $staging /E /XD .venv .git __pycache__ assets migrations\__pycache__ `
    /XF astro.db *.log .env* client_secret*.json credentials*.json *.bak *.p8 *.pem `
    /NFL /NDL /NJH /NJS | Out-Null

# Upload into a scratch directory first, then swap it into place on the VM.
#
# The previous version deleted app/ and migrations/ on the VM BEFORE copying, so
# that a migration removed locally could not linger and give Alembic two heads.
# That is correct until the upload fails: a dropped connection then left the VM
# with no source tree at all and the next build could not run. Uploading to
# /opt/divineastro/.incoming and moving it only after a clean transfer keeps the
# delete-then-replace semantics without the window where nothing exists.
Retry-Remote -What "Preparing the upload directory" -Action {
    gcloud compute ssh $Name --zone $Zone --project $Project --command `
        "sudo rm -rf /opt/divineastro/.incoming && sudo mkdir -p /opt/divineastro/.incoming && sudo chown -R `$(whoami) /opt/divineastro/.incoming"
}

Retry-Remote -What "Uploading the application" -Action {
    gcloud compute scp --recurse "$staging\*" "${Name}:/opt/divineastro/.incoming/" --zone $Zone --project $Project
}

# Transfer succeeded, so it is now safe to replace the tree.
Retry-Remote -What "Swapping the release into place" -Action {
    $cmd = @"
set -e
cd /opt/divineastro
if [ -d .incoming ]; then
  sudo rm -rf app migrations tests
  sudo cp -a .incoming/. .
  sudo rm -rf .incoming
fi
test -d app && test -d migrations
"@ -replace "`r", ""
    gcloud compute ssh $Name --zone $Zone --project $Project --command $cmd
}

# Production values, never the development .env — that one carries a throwaway
# secret key, ASTRO_DEV_LOGIN=1 and no Postgres password.
$envFile = Join-Path $root ".env.production"
if (-not (Test-Path $envFile)) {
    throw ".env.production is missing. Copy deploy\env.production.template to .env.production and fill it in."
}
foreach ($required in @("ASTRO_SECRET_KEY", "POSTGRES_PASSWORD")) {
    $line = Select-String -Path $envFile -Pattern "^$required=.+" -Quiet
    if (-not $line) { throw "$required is empty in .env.production — refusing to deploy." }
}
if (Select-String -Path $envFile -Pattern "^ASTRO_DEV_LOGIN=1" -Quiet) {
    throw "ASTRO_DEV_LOGIN=1 in .env.production — that is the no-password sign-in shortcut. Refusing to deploy."
}
Retry-Remote -What "Uploading .env" -Action {
    gcloud compute scp $envFile "${Name}:/opt/divineastro/.env" --zone $Zone --project $Project
}

Step "Building and starting"
# `set -e` matters: without it a failed image build still exits 0 and the script
# cheerfully reports success while the old container keeps serving.
Retry-Remote -What "Build and start" -Action {
    $cmd = @"
set -e
cd /opt/divineastro
docker compose up -d --build
sleep 20
docker compose ps
"@ -replace "`r", ""
    gcloud compute ssh $Name --zone $Zone --project $Project --command $cmd
}

Step "Verifying the site answers"
$probe = gcloud compute ssh $Name --zone $Zone --project $Project --command `
    "curl -s -o /dev/null -w '%{http_code}' -m 15 https://divineastro.org/api/health || true"
if ($probe -notmatch '200') {
    Write-Warning "Health probe returned '$probe' rather than 200 — the deploy completed but the site may not be serving."
} else {
    Write-Host "  health check: 200" -ForegroundColor Green
}

$ip = gcloud compute addresses describe "$Name-ip" --region ($Zone -replace '-[a-z]$','') --format="value(address)" --project $Project
Write-Host "`nDeployed." -ForegroundColor Green
Write-Host "  Static IP : $ip"
Write-Host "  Next      : point divineastro.org and www at $ip (A records, DNS-only at first)"
Write-Host "  Then      : https://divineastro.org should serve within a minute of DNS resolving"
