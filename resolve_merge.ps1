# Script para resolver conflictos de merge
Set-Location "C:\Users\Mario Cañola\Desktop\PUERTA_ORION"

Write-Host "Verificando estado del repositorio..."
git status

Write-Host "`nVerificando si hay un merge en progreso..."
if (Test-Path ".git\MERGE_HEAD") {
    Write-Host "Merge en progreso detectado"
    
    Write-Host "`nAgregando todos los archivos al staging area..."
    git add .
    
    Write-Host "`nCompletando el merge..."
    git commit --no-edit
    
    Write-Host "`nMerge completado exitosamente!"
} else {
    Write-Host "No hay merge en progreso"
}

Write-Host "`nEstado final del repositorio:"
git status
