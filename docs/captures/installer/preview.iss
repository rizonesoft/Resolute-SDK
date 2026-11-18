; Preview wizard for the installer frame candidates. Installs one text file into a scratch folder, no uninstaller,
; no registry. Driven entirely by /D defines from capture.ps1.
#define Art AddBackslash(ArtDir)

[Setup]
AppId=ResolutePreview-{#Slug}-{#Frame}-{#Theme}
AppName={#AppName}
AppVersion=2.0.0
AppPublisher=Rizonesoft
DefaultDirName={#InstallDir}
PrivilegesRequired=lowest
Uninstallable=no
CreateUninstallRegKey=no
UpdateUninstallLogAppName=no
DisableDirPage=yes
DisableProgramGroupPage=yes
DisableWelcomePage=no
DisableReadyPage=no
DisableFinishedPage=no
OutputDir={#OutDir}
OutputBaseFilename={#Slug}-{#Frame}-{#Theme}
SetupIconFile={#Art}setup-1-graphite-arrow.ico
SetupArchitecture=x64
Compression=lzma2/fast
WizardImageStretch=no
WizardStyle=modern {#Theme} windows11
#if Frame == "a"
WizardImageFile={#Art}a-side-*.png
WizardSmallImageFile={#Art}small-*.png
#elif Frame == "b"
WizardImageFile={#Art}c-side-{#Theme}-*.png
WizardSmallImageFile={#Art}small-*.png
WizardBackImageFile={#Art}b-back-{#Theme}-596.png,{#Art}b-back-{#Theme}-894.png,{#Art}b-back-{#Theme}-1192.png
#else
WizardImageFile={#Art}c-side-{#Theme}-*.png
WizardSmallImageFile=
#endif

[Files]
Source: "{#ArtDir}\spec.txt"; DestDir: "{app}"; Flags: ignoreversion
