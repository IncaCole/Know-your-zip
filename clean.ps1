# General cleanup script for Windows
Write-Host "Starting general cleanup..."

# Directories to clean
$directoriesToClean = @(
    "node_modules",
    "dist",
    "build",
    "out",
    ".next",
    "coverage",
    "logs",
    ".cache",
    "temp",
    "tmp"
)

# File patterns to clean
$filePatternsToClean = @(
    "*.log",
    "*.tmp",
    "*.temp",
    "*.swp",
    "*.swo",
    "Thumbs.db",
    ".DS_Store"
)

# Clean directories
foreach ($dir in $directoriesToClean) {
    if (Test-Path $dir) {
        Write-Host "Removing directory: $dir"
        Remove-Item -Path $dir -Recurse -Force -ErrorAction SilentlyContinue
    }
}

# Clean files
foreach ($pattern in $filePatternsToClean) {
    Get-ChildItem -Path . -Include $pattern -Recurse -Force -ErrorAction SilentlyContinue | 
    ForEach-Object {
        Write-Host "Removing file: $($_.FullName)"
        Remove-Item $_.FullName -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "General cleanup completed!" 