# Script untuk menjalankan Rojo server
# Jalankan dengan: .\serve.ps1

$env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "User") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "Machine")

# Deteksi nama folder saat ini
$projectName = Split-Path -Leaf (Get-Location)

Write-Host "Starting Rojo server..." -ForegroundColor Cyan
Write-Host "Project: $projectName" -ForegroundColor Green
Write-Host "Buka Roblox Studio -> Plugin Rojo -> Connect" -ForegroundColor Yellow
Write-Host ""

rojo serve

Write-Host "Tekan tombol apa saja untuk keluar..." -ForegroundColor DarkGray
Pause
