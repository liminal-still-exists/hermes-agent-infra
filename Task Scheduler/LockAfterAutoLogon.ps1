<#
.SYNOPSIS
    WSL 자동실행을 위한 자동로그인 이후 다시 화면을 잠그기 위한 스크립트. 

.DESCRIPTION
    로그인 절차가 완료되기 전에 화면을 잠그고 바로 해제하면 아직 자격증명이 남아있기 때문에 비밀번호를 묻지 않는 현상이 발생한다. 이를 방지하기 위해 LogonUI.exe 프로세스의 종료를 확인한 뒤에 화면을 잠가야 한다.

.NOTES
    자동로그인 전용이므로 수동 로그인 시에는 아무 동작 없이 즉시 종료된다.
#>

# 1) 자동로그인 여부 확인
try {
    $autoAdminLogon = (Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" -Name AutoAdminLogon -ErrorAction Stop).AutoAdminLogon
} catch {
    $autoAdminLogon = "0"
}
if ($autoAdminLogon -ne "1") {
    exit 0
}

# 2) LogonUI.exe 프로세스 종료 감지
while (Get-Process -Name LogonUI -ErrorAction SilentlyContinue) {
    Start-Sleep -Milliseconds 300
}

# 3) 화면 잠금
rundll32.exe user32.dll,LockWorkStation