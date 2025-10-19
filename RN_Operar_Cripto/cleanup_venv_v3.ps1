# Limpeza do venv_v3_clean

Write-Host "="*80
Write-Host "LIMPEZA: venv_v3_clean → .venv"
Write-Host "="*80
Write-Host ""

Write-Host "ℹ️  O ambiente venv_v3_clean foi usado apenas para testes."
Write-Host "✅ Agora usamos o .venv padrão do projeto."
Write-Host ""

if (Test-Path venv_v3_clean) {
    Write-Host "📦 venv_v3_clean encontrado. Deseja remover? (S/N)"
    $resposta = Read-Host
    
    if ($resposta -eq "S" -or $resposta -eq "s") {
        Write-Host "🗑️  Removendo venv_v3_clean..."
        Remove-Item -Recurse -Force venv_v3_clean
        Write-Host "✅ venv_v3_clean removido com sucesso!"
    } else {
        Write-Host "⏭️  Mantendo venv_v3_clean (pode remover manualmente depois)"
    }
} else {
    Write-Host "✅ venv_v3_clean não encontrado (já removido ou não existia)"
}

Write-Host ""
Write-Host "="*80
Write-Host "✅ Use agora: .\.venv\Scripts\Activate.ps1"
Write-Host "="*80
