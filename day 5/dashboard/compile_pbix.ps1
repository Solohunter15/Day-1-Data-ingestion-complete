# PowerShell Script to Automate Power BI Desktop Compilation & Export
# Launching via file association is necessary for Microsoft Store versions.

$PBIPPath = "c:\Users\jibum\OneDrive\Desktop\Bluestock Internship\dashboard\bluestock_mf_dashboard.pbip"
$PBIXPath = "c:\Users\jibum\OneDrive\Desktop\Bluestock Internship\bluestock_mf_dashboard.pbix"

Write-Host "=================================================="
Write-Host "STARTING POWER BI COMPILATION HARNESS (ASSOCIATION)"
Write-Host "=================================================="

# Remove old PBIX if exists to prevent override prompts
if (Test-Path $PBIXPath) {
    Remove-Item $PBIXPath -Force
    Write-Host "Removed existing bluestock_mf_dashboard.pbix."
}

$wshell = New-Object -ComObject Wscript.Shell

$signature = @"
[DllImport("user32.dll")]
public static extern bool SetForegroundWindow(IntPtr hWnd);
[DllImport("user32.dll")]
public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
[DllImport("user32.dll")]
public static extern IntPtr GetForegroundWindow();
[DllImport("user32.dll", CharSet = CharSet.Auto, SetLastError = true)]
public static extern int GetWindowText(IntPtr hWnd, System.Text.StringBuilder lpString, int nMaxCount);
[DllImport("user32.dll")]
public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);
"@
Add-Type -MemberDefinition $signature -Name "Win32UtilsV3" -Namespace "Win32V3" -ErrorAction SilentlyContinue

function Get-ActiveWindowProcessId {
    $hwnd = [Win32V3.Win32UtilsV3]::GetForegroundWindow()
    [uint32]$activeProcessId = 0
    [Win32V3.Win32UtilsV3]::GetWindowThreadProcessId($hwnd, [ref]$activeProcessId) | Out-Null
    return $activeProcessId
}

function Get-ActiveWindowTitle {
    $hwnd = [Win32V3.Win32UtilsV3]::GetForegroundWindow()
    $sb = New-Object System.Text.StringBuilder 256
    $len = [Win32V3.Win32UtilsV3]::GetWindowText($hwnd, $sb, 256)
    return $sb.ToString()
}

function Focus-PowerBI {
    $proc = Get-Process -Name "PBIDesktop" -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($proc) {
        $wshell = New-Object -ComObject Wscript.Shell
        for ($i = 1; $i -le 5; $i++) {
            Write-Host "Focus attempt $i of 5..."
            
            # Use AppActivate first as it is very reliable for PID
            $wshell.AppActivate($proc.Id) | Out-Null
            Start-Sleep -Milliseconds 300
            
            # If MainWindowHandle is non-zero, try ShowWindow/SetForegroundWindow as well
            if ($proc.MainWindowHandle -ne 0) {
                [Win32V3.Win32UtilsV3]::ShowWindow($proc.MainWindowHandle, 9) | Out-Null # SW_RESTORE
                Start-Sleep -Milliseconds 100
                [Win32V3.Win32UtilsV3]::SetForegroundWindow($proc.MainWindowHandle) | Out-Null
                Start-Sleep -Milliseconds 100
            }
            
            $activePid = Get-ActiveWindowProcessId
            $activeTitle = Get-ActiveWindowTitle
            if ($activePid -eq $proc.Id) {
                Write-Host "Successfully focused Power BI (PID: $activePid, Title: '$activeTitle')"
                return $true
            }
            Write-Warning "Focus failed (Active window PID: $activePid, Title: '$activeTitle'). Target PID is $($proc.Id)."
        }
        Write-Error "Failed to focus Power BI after multiple attempts."
        return $false
    }
    Write-Warning "PBIDesktop process not found."
    return $false
}

Write-Host "Launching Power BI Desktop by opening project file..."
Start-Process -FilePath $PBIPPath

# Wait for Power BI Desktop to load
Write-Host "Waiting for Power BI to initialize (45 seconds)..."
Start-Sleep -Seconds 45

# Capture launch state
python -c "from PIL import ImageGrab; ImageGrab.grab().save('dashboard/step1_launch.png')"
Write-Host "Saved step1_launch.png"

# Focus main window
$focused = Focus-PowerBI
if (-not $focused) { Write-Error "Focus failed. Exiting."; Exit 1 }
Start-Sleep -Seconds 2

# Dismiss splash screen / any startup popups
Write-Host "Dismissing splash screen..."
$wshell.SendKeys("{ESC}")
Start-Sleep -Seconds 2
$wshell.SendKeys("{ESC}")
Start-Sleep -Seconds 3

# Capture post-dismiss state
python -c "from PIL import ImageGrab; ImageGrab.grab().save('dashboard/step2_dismiss.png')"
Write-Host "Saved step2_dismiss.png"

# Trigger Data Refresh (using F5)
$focused = Focus-PowerBI
if (-not $focused) { Write-Error "Focus failed. Exiting."; Exit 1 }
Write-Host "Triggering Data Refresh (F5)..."
$wshell.SendKeys("{F5}")
Start-Sleep -Seconds 25 # Wait for refresh to complete

# Capture post-refresh state
python -c "from PIL import ImageGrab; ImageGrab.grab().save('dashboard/step2_post_refresh.png')"
Write-Host "Saved step2_post_refresh.png"

# Dismiss any warnings/refresh dialogs if open
$focused = Focus-PowerBI
if (-not $focused) { Write-Error "Focus failed. Exiting."; Exit 1 }
$wshell.SendKeys("{ESC}")
Start-Sleep -Seconds 2

# Save As PBIX
Write-Host "Saving project as standalone PBIX..."
$focused = Focus-PowerBI
if (-not $focused) { Write-Error "Focus failed. Exiting."; Exit 1 }
Start-Sleep -Seconds 2

$wshell.SendKeys("{F12}") # F12 (Save As)
Start-Sleep -Seconds 3

# Capture Save As dialog state
python -c "from PIL import ImageGrab; ImageGrab.grab().save('dashboard/step3_save_as_dialog.png')"
Write-Host "Saved step3_save_as_dialog.png"

# Focus Save as type dropdown (TAB x2)
Write-Host "Focusing Save as type dropdown (TAB x2)..."
$wshell.SendKeys("{TAB}{TAB}")
Start-Sleep -Seconds 1

# Select first option (*.pbix) using Home
$wshell.SendKeys("{HOME}")
Start-Sleep -Seconds 1

# Focus File name input box back (Shift+TAB x2)
Write-Host "Focusing File name input box back (Shift+TAB x2)..."
$wshell.SendKeys("+{TAB}+{TAB}")
Start-Sleep -Seconds 1

# Type the save path
Write-Host "Typing path: $PBIXPath"
$wshell.SendKeys($PBIXPath)
Start-Sleep -Seconds 1

# Capture typed path and selected type state
python -c "from PIL import ImageGrab; ImageGrab.grab().save('dashboard/step4_typed_path.png')"
Write-Host "Saved step4_typed_path.png"

# Submit Save (ENTER)
Write-Host "Submitting Save (ENTER)..."
$wshell.SendKeys("{ENTER}")
Start-Sleep -Seconds 10 # Wait for save to complete

# Capture post-save state
python -c "from PIL import ImageGrab; ImageGrab.grab().save('dashboard/step5_after_enter.png')"
Write-Host "Saved step5_after_enter.png"

# Close Power BI Desktop
Write-Host "Compilation complete. Closing Power BI Desktop..."
Stop-Process -Name "PBIDesktop" -Force

Write-Host "=================================================="
Write-Host "POWER BI COMPILATION PROCESS COMPLETE!"
if (Test-Path $PBIXPath) {
    Write-Host "Saved successfully: $PBIXPath"
} else {
    Write-Warning "Save failed. PBIX file was not generated."
}
Write-Host "=================================================="
