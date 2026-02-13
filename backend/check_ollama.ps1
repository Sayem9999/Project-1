# Check if Ollama is running and Llama 3.2 is available
Write-Host "--- AI Readiness Check (Ollama) ---" -ForegroundColor Cyan

$ollamaUrl = "http://localhost:11434/api/tags"
try {
    $response = Invoke-RestMethod -Uri $ollamaUrl -Method Get -ErrorAction Stop
    Write-Host "Ollama is running. [OK]" -ForegroundColor Green
    
    $models = $response.models | Select-Object -ExpandProperty name
    if ($models -contains "llama3.2:3b" -or $models -contains "llama3.2:latest") {
        Write-Host "Llama 3.2 (3B) is available. [OK]" -ForegroundColor Green
    } else {
        Write-Host "Llama 3.2 (3B) is NOT found in local library." -ForegroundColor Yellow
        Write-Host "Hint: Run 'ollama pull llama3.2:3b' in your terminal." -ForegroundColor Gray
    }
}
catch {
    Write-Host "Ollama is NOT running at http://localhost:11434" -ForegroundColor Red
    Write-Host "Please start Ollama Desktop or run 'ollama serve' before using Proedit AI features." -ForegroundColor Yellow
}

Write-Host "`nPress any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
