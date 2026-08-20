$indexContent = [System.IO.File]::ReadAllText("index.html")
if ($indexContent -match '(?s)(<footer.*?>.*?</footer>)') {
    $footer = $matches[1]
    $files = Get-ChildItem *.html | Where-Object Name -ne 'index.html'
    foreach ($f in $files) {
        $content = [System.IO.File]::ReadAllText($f.FullName)
        $newContent = $content -replace '(?s)<footer.*?>.*?</footer>', $footer
        [System.IO.File]::WriteAllText($f.FullName, $newContent)
    }
    Write-Host "Replaced all footers successfully!"
} else {
    Write-Host "Footer not found in index.html"
}
