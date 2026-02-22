# PowerShell TCP Client Test Script
$client = New-Object System.Net.Sockets.TcpClient
$client.Connect('localhost', 4000)
$stream = $client.GetStream()
$writer = New-Object System.IO.StreamWriter($stream)
$reader = New-Object System.IO.StreamReader($stream)

Start-Sleep -Milliseconds 500

$writer.WriteLine('test')
$writer.Flush()

Start-Sleep -Milliseconds 500

$response = $reader.ReadToEnd()
Write-Host "Response: $response"

$client.Close()
