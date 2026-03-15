$ErrorActionPreference = 'Stop'

$jobVerseRoot = $PSScriptRoot
$agenticRoot = Join-Path (Split-Path $jobVerseRoot -Parent) 'Agentic_Job_Search-main'
$appPath = Join-Path $agenticRoot 'app.py'

if (-not (Test-Path $appPath)) {
    Write-Error "Could not find Streamlit app at: $appPath"
}

Push-Location $agenticRoot
try {
    Write-Host "Starting Agentic Job Search Streamlit app at http://localhost:8501 ..."
    streamlit run app.py
}
finally {
    Pop-Location
}
