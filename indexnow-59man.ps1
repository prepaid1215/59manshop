param(
  [ValidateSet('sitemap','single')][string]$Mode = 'sitemap',
  [string]$Url = '',
  [switch]$DryRun
)
$ErrorActionPreference = 'Stop'
$site = 'https://www.59man.shop'
$hostName = 'www.59man.shop'
$key = 'b10edb20efd14a1666dd9f0930f45ac5'
$keyLocation = "$site/$key.txt"
$endpoint = 'https://searchadvisor.naver.com/indexnow'
try {
  [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
  Write-Host 'Verifying the published IndexNow key...' 
  $keyResponse = Invoke-WebRequest -Uri $keyLocation -UseBasicParsing -TimeoutSec 25
  if ([int]$keyResponse.StatusCode -ne 200 -or $keyResponse.Content.Trim() -cne $key) {
    throw "The published key file is missing or incorrect: $keyLocation"
  }
  if ($Mode -eq 'single') {
    if ([string]::IsNullOrWhiteSpace($Url)) { throw 'Enter a full HTTPS URL.' }
    $requested = @($Url.Trim())
  } else {
    Write-Host 'Fetching the LIVE sitemap...' 
    $response = Invoke-WebRequest -Uri "$site/sitemap.xml" -UseBasicParsing -TimeoutSec 30
    [xml]$document = $response.Content
    $requested = @($document.GetElementsByTagName('loc') | ForEach-Object { $_.InnerText.Trim() })
  }
  $list = New-Object 'System.Collections.Generic.List[string]'
  foreach ($address in $requested) {
    if ([string]::IsNullOrWhiteSpace($address)) { continue }
    $parsed = $null
    if (-not [Uri]::TryCreate($address, [UriKind]::Absolute, [ref]$parsed)) {
      throw "Invalid URL: $address"
    }
    if ($parsed.Scheme -cne 'https' -or $parsed.Host -cne $hostName -or $parsed.Port -ne 443) {
      throw "The URL must belong to https://$hostName: $address"
    }
    if ($parsed.Query -or $parsed.Fragment) { throw "Remove query strings and fragments: $address" }
    $list.Add($parsed.AbsoluteUri)
  }
  $urls = @($list | Sort-Object -Unique)
  if ($urls.Count -eq 0) { throw 'The selected list has no URLs.' }
  Write-Host ('URLs: ' + $urls.Count)
  if ($DryRun) {
    foreach ($item in $urls) { Write-Host ('DRY RUN: ' + $item) }
    Write-Host 'No request was sent.'
    exit 0
  }
  $body = @{ host = $hostName; key = $key; keyLocation = $keyLocation; urlList = $urls } | ConvertTo-Json -Depth 4 -Compress
  $payload = [System.Text.Encoding]::UTF8.GetBytes($body)
  Write-Host 'Submitting to Naver IndexNow...' 
  $sent = Invoke-WebRequest -Uri $endpoint -Method Post -Body $payload -ContentType 'application/json; charset=utf-8' -UseBasicParsing -TimeoutSec 40
  $status = [int]$sent.StatusCode
  Write-Host ('HTTP response: ' + $status)
  if ($status -ne 200 -and $status -ne 202) { throw ('Unexpected HTTP status: ' + $status) }
  Write-Host 'Submission accepted. Search indexing is NOT guaranteed.'
  exit 0
} catch {
  Write-Host ('ERROR: ' + $_.Exception.Message) -ForegroundColor Red
  exit 1
}
