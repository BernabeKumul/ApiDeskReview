# Test script using curl for AI Process endpoint

Write-Host "🧪 Testing AI Process Endpoint" -ForegroundColor Green
Write-Host "=" * 50

# Wait for server to start
Start-Sleep 8

# Test health endpoint
Write-Host "`n1. Testing AI Process Health Check..." -ForegroundColor Yellow
try {
    $healthResponse = curl.exe -s http://127.0.0.1:8000/ai-process/health
    Write-Host "Health Response: $healthResponse" -ForegroundColor Green
} catch {
    Write-Host "Health check failed: $_" -ForegroundColor Red
}

# Test audit processing endpoint
Write-Host "`n2. Testing Audit Processing..." -ForegroundColor Yellow

$testData = @{
    "AuditID" = 123
    "OrgID" = 456
    "Operation" = "Test Farm Operation"
    "Products" = "Strawberries"
    "Documents" = @(
        @{
            "QuestionID" = 1
            "DocumentsId" = @(
                @{
                    "DocumentId" = 1
                    "URL" = "https://example.com/hola.pdf"
                },
                @{
                    "DocumentId" = 2
                    "URL" = "https://example.com/hola2.pdf"
                }
            )
        }
    )
} | ConvertTo-Json -Depth 5

try {
    $auditResponse = curl.exe -s -X POST -H "Content-Type: application/json" -d $testData http://127.0.0.1:8000/ai-process/audit
    Write-Host "Audit Response: $auditResponse" -ForegroundColor Green
} catch {
    Write-Host "Audit processing failed: $_" -ForegroundColor Red
}

Write-Host "`n✅ Test completed!" -ForegroundColor Green