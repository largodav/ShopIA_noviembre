param(
    [switch]$UseNvidiaProfile,
    [switch]$UseTailscaleProfile
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$InfraDir = (Resolve-Path (Join-Path $ScriptDir "..\..")).Path
$ComposeFile = Join-Path $InfraDir "docker-compose.yml"
$EnvFile = Join-Path $InfraDir ".env"

$Profiles = ""
if ($UseNvidiaProfile) { $Profiles += " --profile nvidia" }
if ($UseTailscaleProfile) { $Profiles += " --profile tailscale" }

$Arguments = "compose -f `"$ComposeFile`" --env-file `"$EnvFile`"$Profiles up -d"
$Action = New-ScheduledTaskAction -Execute "docker" -Argument $Arguments
$Trigger = New-ScheduledTaskTrigger -AtLogOn
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask `
    -TaskName "ShopIA-Backend" `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Description "Inicia automáticamente el stack Docker de ShopIA al iniciar Windows." `
    -Force

Write-Host "Tarea programada 'ShopIA-Backend' registrada correctamente."
