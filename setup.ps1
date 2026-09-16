<#
.SYNOPSIS
    Regenerate local assets for the afsarudeen profile README.

.EXAMPLE
    .\setup.ps1 -Image .\me.jpg -Color -Reveal

.EXAMPLE
    # skill + language radars only
    .\setup.ps1 -Username afsarudeen
#>
[CmdletBinding()]
param(
    [string]$Username = 'afsarudeen',
    [string]$Image,
    [ValidateSet('dots', 'binary', 'ascii', 'braille')]
    [string]$Mode = 'dots',
    [int]$Cols = 100,
    [switch]$Circle,
    [switch]$Color,
    [switch]$Animate,
    [switch]$Reveal,
    [switch]$Invert,
    [switch]$Square,
    [string]$Focus = '0.5,0.5'
)

$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot

Write-Host "`n[1/3] drawing the skill radar" -ForegroundColor Cyan
python (Join-Path $root 'scripts\radar.py') --data (Join-Path $root 'assets\skills.json') -o (Join-Path $root 'assets\radar')

if ($Username) {
    Write-Host "      drawing the language radar from the GitHub API" -ForegroundColor Cyan
    try {
        python (Join-Path $root 'scripts\radar.py') --github $Username -o (Join-Path $root 'assets\radar-langs') --values --curve 0.4
    } catch {
        Write-Warning "language radar skipped: $_"
    }

    Write-Host "      drawing stat / repo cards" -ForegroundColor Cyan
    try {
        python (Join-Path $root 'scripts\cards.py') --user $Username --projects (Join-Path $root 'assets\projects.json') --out (Join-Path $root 'assets')
        python (Join-Path $root 'scripts\local_cards.py') --projects (Join-Path $root 'assets\projects.json') --out (Join-Path $root 'assets')
    } catch {
        Write-Warning "cards skipped: $_"
    }
}

if ($Image) {
    Write-Host "`n[2/3] dot-matrixing $Image" -ForegroundColor Cyan
    $dotArgs = @(
        (Join-Path $root 'scripts\dotify.py'), $Image,
        '-o', (Join-Path $root 'assets\portrait'),
        '--mode', $Mode, '--cols', $Cols, '--equalize', '--detail', '0.5'
    )
    if ($Square)  { $dotArgs += @('--square', '--focus', $Focus) }
    if ($Circle)  { $dotArgs += '--circle' }
    if ($Color)   { $dotArgs += '--color' }
    if ($Animate) { $dotArgs += '--animate' }
    if ($Reveal)  { $dotArgs += '--reveal' }
    if ($Invert)  { $dotArgs += '--invert' }
    python @dotArgs
} else {
    Write-Host "`n[2/3] no -Image given, keeping existing portrait" -ForegroundColor DarkGray
}

Write-Host "`n[3/3] done. open preview.html, then read SETUP.md for the GitHub Actions side.`n" -ForegroundColor Green
