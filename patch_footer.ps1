$indexContent = Get-Content index.html -Raw
if ($indexContent -match '(?s)(<footer.*?>.*?</footer>)') {
    $footer = $matches[1]
    $files = Get-ChildItem *.html | Where-Object Name -ne 'index.html'
    foreach ($f in $files) {
        $content = Get-Content $f.FullName -Raw
        $newContent = $content -replace '(?s)<footer.*?>.*?</footer>', $footer
        Set-Content -Path $f.FullName -Value $newContent -Encoding UTF8
    }
    Write-Host "Replaced all footers successfully!"
} else {
    Write-Host "Footer not found in index.html"
}
