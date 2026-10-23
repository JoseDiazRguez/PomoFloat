#define MyAppName "PomoFloat"
#define MyAppVersion "0.1.0"
#define MyAppPublisher "PomoFloat"
#define MyAppExeName "PomoFloat.exe"

[Setup]
AppId={{6D87B512-00A7-4E5D-A54F-7C2A8A987F10}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}

DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}

OutputDir=..\..\dist\installer
OutputBaseFilename=PomoFloat-{#MyAppVersion}-Setup

Compression=lzma2
SolidCompression=yes

WizardStyle=modern

ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

PrivilegesRequired=lowest

UninstallDisplayName={#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}

[Files]
Source: "..\..\dist\PomoFloat\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\PomoFloat"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\PomoFloat"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el escritorio"; GroupDescription: "Accesos directos:"; Flags: unchecked

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Ejecutar PomoFloat"; Flags: nowait postinstall skipifsilent