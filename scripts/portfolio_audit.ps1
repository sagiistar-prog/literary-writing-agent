$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $Root

$failures = New-Object System.Collections.Generic.List[string]
$warnings = New-Object System.Collections.Generic.List[string]

function Add-Failure {
    param([string]$Message)
    [void]$failures.Add($Message)
}

function Add-Warning {
    param([string]$Message)
    [void]$warnings.Add($Message)
}

function Test-CommandExists {
    param([string]$Name)
    return $null -ne (Get-Command $Name -ErrorAction SilentlyContinue)
}

function Invoke-Git {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$GitArgs)
    $previousPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $output = & git -c "safe.directory=$Root" @GitArgs 2>$null
    }
    finally {
        $ErrorActionPreference = $previousPreference
    }
    return @{
        Code = $LASTEXITCODE
        Output = $output
    }
}

function Get-RepoFiles {
    $inside = Invoke-Git "rev-parse" "--is-inside-work-tree"
    if ($inside.Code -eq 0) {
        $tracked = & git -c "safe.directory=$Root" ls-files
        if ($LASTEXITCODE -eq 0 -and $tracked.Count -gt 0) {
            return @($tracked | Where-Object { $_ -and (Test-Path -LiteralPath $_ -PathType Leaf) })
        }
    }

    Add-Warning "No tracked files found yet; scanning candidate project files only."
    $excluded = @(".git", ".venv", "output", "work", "raw")
    $files = Get-ChildItem -LiteralPath $Root -Recurse -File -Force | Where-Object {
        $relative = Resolve-Path -LiteralPath $_.FullName -Relative
        foreach ($part in $excluded) {
            if ($relative -match "(^|[\\/])$([regex]::Escape($part))([\\/]|$)") {
                return $false
            }
        }
        return $true
    }
    return @($files | ForEach-Object { Resolve-Path -LiteralPath $_.FullName -Relative })
}

function Get-TextContent {
    param([string]$Path)
    try {
        return Get-Content -LiteralPath $Path -Raw -Encoding UTF8
    }
    catch {
        Add-Warning "Could not read as UTF-8: $Path"
        return ""
    }
}

function New-TextFromCodePoints {
    param([int[]]$CodePoints)
    return -join ($CodePoints | ForEach-Object { [char]$_ })
}

function Test-GitHubPublic {
    $inside = Invoke-Git "rev-parse" "--is-inside-work-tree"
    if ($inside.Code -ne 0) {
        Add-Warning "Git repository not initialized yet; public visibility check deferred."
        return
    }

    $remote = Invoke-Git "remote" "get-url" "origin"
    if ($remote.Code -ne 0 -or -not $remote.Output) {
        Add-Warning "No origin remote found yet; public visibility check deferred."
        return
    }

    if (-not (Test-CommandExists "gh")) {
        Add-Warning "GitHub CLI not found; public visibility check could not run."
        return
    }

    $remoteText = ($remote.Output | Select-Object -First 1).Trim()
    $repo = $remoteText
    $repo = $repo -replace "^git@github.com:", ""
    $repo = $repo -replace "^https://github.com/", ""
    $repo = $repo -replace "\.git$", ""

    if (-not $repo -or $repo -notmatch "/") {
        Add-Warning "Could not parse GitHub repository from origin remote."
        return
    }

    $json = & gh repo view $repo --json nameWithOwner,visibility,url 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $json) {
        Add-Warning "GitHub visibility check could not reach the remote repository."
        return
    }

    $info = $json | ConvertFrom-Json
    if ($info.visibility -ne "PUBLIC") {
        Add-Failure "GitHub repository is not PUBLIC: $($info.nameWithOwner)"
    }
    else {
        Write-Output "GitHub repository public: $($info.url)"
    }
}

function Test-GitSync {
    $inside = Invoke-Git "rev-parse" "--is-inside-work-tree"
    if ($inside.Code -ne 0) {
        Add-Warning "Git repository not initialized yet; sync check deferred."
        return
    }

    $status = & git -c "safe.directory=$Root" status --porcelain
    if ($LASTEXITCODE -eq 0 -and $status.Count -gt 0) {
        Add-Warning "Working tree has uncommitted changes."
    }

    $upstream = Invoke-Git "rev-parse" "--abbrev-ref" "--symbolic-full-name" "@{u}"
    if ($upstream.Code -ne 0) {
        Add-Warning "No upstream branch configured yet; sync check deferred."
        return
    }

    $syncResult = Invoke-Git "rev-list" "--left-right" "--count" "HEAD...@{u}"
    $counts = $syncResult.Output
    if ($syncResult.Code -ne 0 -or -not $counts) {
        Add-Warning "Could not compare local and remote history."
        return
    }

    $parts = ($counts -split "\s+")
    if ($parts.Count -ge 2) {
        $ahead = [int]$parts[0]
        $behind = [int]$parts[1]
        if ($ahead -ne 0 -or $behind -ne 0) {
            Add-Failure "Local and remote are not synchronized. Ahead: $ahead Behind: $behind"
        }
    }
}

function Test-FileInventory {
    param([string[]]$Files)

    $blockedExtensions = @(".pdf", ".docx", ".xlsx", ".zip", ".mp4", ".mov", ".mkv", ".wav", ".mp3")
    foreach ($file in $Files) {
        $extension = [System.IO.Path]::GetExtension($file).ToLowerInvariant()
        if ($blockedExtensions -contains $extension) {
            Add-Failure "Blocked file type found: $file"
        }

        $item = Get-Item -LiteralPath $file -ErrorAction SilentlyContinue
        if ($item -and $item.Length -gt 5MB) {
            Add-Failure "Large file found over 5 MB: $file"
        }
    }
}

function Test-TextRisks {
    param([string[]]$Files)

    $literalPatterns = @(
        ("Euro" + "link"),
        ("New" + " " + "Fada"),
        ("RX" + " " + "Consult"),
        (New-TextFromCodePoints @(0x771F, 0x5B9E, 0x5BA2, 0x6237)),
        (New-TextFromCodePoints @(0x771F, 0x5B9E, 0x5408, 0x4F5C, 0x65B9)),
        (New-TextFromCodePoints @(0x5546, 0x4E1A, 0x95ED, 0x73AF)),
        (New-TextFromCodePoints @(0x76C8, 0x5229, 0x6A21, 0x5F0F)),
        (New-TextFromCodePoints @(0x8BA2, 0x9605)),
        (New-TextFromCodePoints @(0x70B9, 0x6570)),
        ("C" + "RM"),
        (New-TextFromCodePoints @(0x5185, 0x90E8, 0x8DEF, 0x5F84)),
        (New-TextFromCodePoints @(0x6A21, 0x4EFF, 0x67D0, 0x4F4D, 0x5728, 0x4E16, 0x4F5C, 0x5BB6, 0x98CE, 0x683C)),
        (New-TextFromCodePoints @(0x674E, 0x5A1F, 0x98CE, 0x683C)),
        (New-TextFromCodePoints @(0x4F59, 0x534E, 0x98CE, 0x683C)),
        (New-TextFromCodePoints @(0x83AB, 0x8A00, 0x98CE, 0x683C)),
        (New-TextFromCodePoints @(0x77E5, 0x540D, 0x4F5C, 0x54C1, 0x539F, 0x6587)),
        (New-TextFromCodePoints @(0x539F, 0x6587, 0x6458, 0x5F55))
    )

    $regexPatterns = @(
        ("gh" + "p_" + "[A-Za-z0-9_]{8,}"),
        ("github" + "_pat_" + "[A-Za-z0-9_]{8,}"),
        ("ANTHROPIC" + "_AUTH" + "_TOKEN"),
        ("(?<![A-Za-z])" + "sk" + "-[A-Za-z0-9_-]{8,}"),
        "[A-Za-z]:\\Users",
        ("Sagi" + "stariam")
    )

    foreach ($file in $Files) {
        $extension = [System.IO.Path]::GetExtension($file).ToLowerInvariant()
        if ($extension -in @(".png", ".jpg", ".jpeg", ".gif", ".ico", ".bin")) {
            continue
        }

        $content = Get-TextContent $file
        if (-not $content) {
            continue
        }

        foreach ($pattern in $literalPatterns) {
            if ($content.Contains($pattern)) {
                Add-Failure "Sensitive phrase found in $file"
            }
        }

        foreach ($pattern in $regexPatterns) {
            if ($content -match $pattern) {
                Add-Failure "Sensitive token or local path pattern found in $file"
            }
        }
    }
}

Write-Output "Portfolio audit root: $Root"
$files = Get-RepoFiles
Write-Output "Files scanned: $($files.Count)"

Test-GitHubPublic
Test-GitSync
Test-FileInventory $files
Test-TextRisks $files

if ($warnings.Count -gt 0) {
    Write-Output ""
    Write-Output "WARNINGS:"
    $warnings | ForEach-Object { Write-Output "- $_" }
}

if ($failures.Count -gt 0) {
    Write-Output ""
    Write-Output "FAILURES:"
    $failures | ForEach-Object { Write-Output "- $_" }
    Write-Output ""
    Write-Output "AUDIT RESULT: FAIL"
    exit 1
}

Write-Output ""
Write-Output "AUDIT RESULT: PASS"
exit 0
