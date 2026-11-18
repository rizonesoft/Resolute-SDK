param([string]$Root)
# Compiles each preview setup, runs it, captures Welcome, Ready and Finished by clicking its own buttons, then closes it.
$ErrorActionPreference = 'Stop'
Add-Type -ReferencedAssemblies System.Drawing -TypeDefinition @'
using System; using System.Text; using System.Drawing; using System.Drawing.Imaging; using System.Runtime.InteropServices;
using System.Collections.Generic;
public static class Win {
  public delegate bool EnumProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc f, IntPtr l);
  [DllImport("user32.dll")] public static extern bool EnumChildWindows(IntPtr p, EnumProc f, IntPtr l);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] public static extern IntPtr SendMessage(IntPtr h, uint m, IntPtr w, IntPtr l);
  [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr h, uint m, IntPtr w, IntPtr l);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr dc, uint f);
  [DllImport("user32.dll")] public static extern bool SetProcessDpiAwarenessContext(IntPtr v);
  [DllImport("dwmapi.dll")] public static extern int DwmGetWindowAttribute(IntPtr h, int a, out RECT r, int s);
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L, T, R, B; }
  public static string Text(IntPtr h) { var s = new StringBuilder(256); GetWindowText(h, s, 256); return s.ToString(); }
  public static IntPtr Find(string title) {
    IntPtr found = IntPtr.Zero;
    EnumWindows((h, l) => { if (IsWindowVisible(h) && Text(h) == title) { found = h; return false; } return true; }, IntPtr.Zero);
    return found;
  }
  public static IntPtr Button(IntPtr top, string text) {
    IntPtr found = IntPtr.Zero;
    EnumChildWindows(top, (h, l) => { if (IsWindowVisible(h) && Text(h) == text) { found = h; return false; } return true; }, IntPtr.Zero);
    return found;
  }
  public static void Click(IntPtr b) { PostMessage(b, 0x00F5, IntPtr.Zero, IntPtr.Zero); }
  public static void Shot(IntPtr h, string path) {
    RECT w; GetWindowRect(h, out w); RECT f; DwmGetWindowAttribute(h, 9, out f, Marshal.SizeOf(typeof(RECT)));
    using (var bmp = new Bitmap(w.R - w.L, w.B - w.T)) {
      using (var g = Graphics.FromImage(bmp)) { var dc = g.GetHdc(); PrintWindow(h, dc, 2); g.ReleaseHdc(dc); }
      var crop = new Rectangle(f.L - w.L, f.T - w.T, f.R - f.L, f.B - f.T);
      using (var c = bmp.Clone(crop, bmp.PixelFormat)) c.Save(path, ImageFormat.Png);
    }
  }
}
'@
[Win]::SetProcessDpiAwarenessContext([IntPtr](-4)) | Out-Null
$iscc = Join-Path $Root 'inno\ISCC.exe'
$shots = Join-Path $Root 'shots'; New-Item -ItemType Directory -Force $shots | Out-Null
$build = Join-Path $Root 'setups'; New-Item -ItemType Directory -Force $build | Out-Null
$tools = @{ memboost = 'MemBoost'; firemin = 'Firemin' }

function Wait-Button($title, $text, $seconds = 20) {
  $end = (Get-Date).AddSeconds($seconds)
  while ((Get-Date) -lt $end) {
    $w = [Win]::Find($title); if ($w -ne [IntPtr]::Zero) { $b = [Win]::Button($w, $text); if ($b -ne [IntPtr]::Zero) { return @($w, $b) } }
    Start-Sleep -Milliseconds 150
  }
  throw "timed out waiting for '$text' in '$title'"
}

foreach ($slug in $tools.Keys) {
  $name = $tools[$slug]; $art = Join-Path $Root "art-out\$slug"
  foreach ($frame in 'a','b','c') { foreach ($theme in 'light','dark') {
    $id = "$slug-$frame-$theme"
    $dir = Join-Path $Root "preview-install\$id"
    & $iscc --quiet "/DSlug=$slug" "/DAppName=$name" "/DFrame=$frame" "/DTheme=$theme" "/DArtDir=$art" "/DInstallDir=$dir" "/DOutDir=$build" (Join-Path $Root 'installer-art\preview.iss')
    if ($LASTEXITCODE -ne 0) { throw "ISCC failed for $id" }
    $p = Start-Process (Join-Path $build "$id.exe") -PassThru
    try {
      $title = "Setup - $name"
      $w, $b = Wait-Button $title '&Next'; Start-Sleep -Milliseconds 700; [Win]::Shot($w, "$shots\$id-1-welcome.png"); [Win]::Click($b)
      $w, $b = Wait-Button $title '&Install'; Start-Sleep -Milliseconds 700; [Win]::Shot($w, "$shots\$id-2-ready.png"); [Win]::Click($b)
      $w, $b = Wait-Button $title '&Finish' 60; Start-Sleep -Milliseconds 700; [Win]::Shot($w, "$shots\$id-3-finish.png"); [Win]::Click($b)
      $p.WaitForExit(15000) | Out-Null
      "captured $id"
    } finally {
      if (-not $p.HasExited) { taskkill /T /F /PID $p.Id 2>&1 | Out-Null }
      Get-Process | Where-Object { $_.Path -like "*\Temp\is-*\$id.tmp" } | ForEach-Object { taskkill /T /F /PID $_.Id 2>&1 | Out-Null }
    }
  } }
}
