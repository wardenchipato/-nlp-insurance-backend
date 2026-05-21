# Scrape accident-related articles into knowledge/ (see scrape_sources.yaml).
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $here

$py = Get-Command py -ErrorAction SilentlyContinue
if (-not $py) {
    $py = Get-Command python -ErrorAction SilentlyContinue
}
if (-not $py) {
    Write-Error "Python not found. Install Python 3 and ensure 'py' or 'python' is on PATH."
    exit 1
}

& $py.Source @("scripts/run_scraper.py") + $args
exit $LASTEXITCODE
