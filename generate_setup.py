"""
Скрипт для генерации файла setup.iss для Inno Setup с актуальной версией.
"""
import os
import uuid
from version import __version__

def generate_guid():
    """Генерация уникального GUID для AppId."""
    return str(uuid.uuid4()).upper()

def generate_setup_iss():
    """Генерация файла setup.iss с актуальной версией."""
    
    # Генерируем GUID для AppId
    app_id = generate_guid()
    
    # Шаблон с плейсхолдерами VERSION и APP_ID
    template = """; Inno Setup Script для ChatList
; Сгенерировано автоматически скриптом generate_setup.py
; Версия: VERSION

#define MyAppName "ChatList"
#define MyAppVersion "VERSION"
#define MyAppPublisher "ChatList"
#define MyAppURL "https://github.com/yourusername/chatlist"
#define MyAppExeName "ChatList-vVERSION.exe"
#define MyAppId "APP_ID"

[Setup]
; Основные настройки
AppId={#MyAppId}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=LICENSE
OutputDir=installer
OutputBaseFilename=ChatList-Setup-v{#MyAppVersion}
SetupIconFile=app.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
Source: "dist\ChatList-vVERSION.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}\logs"
Type: filesandordirs; Name: "{app}\chatlist.db"
Type: filesandordirs; Name: "{app}\*.log"
Type: dirifempty; Name: "{app}"

[Code]
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  LogsDir: string;
  DbFile: string;
begin
  if CurUninstallStep = usUninstall then
  begin
    LogsDir := ExpandConstant('{app}\logs');
    DbFile := ExpandConstant('{app}\chatlist.db');
    
    // Удаление директории логов
    if DirExists(LogsDir) then
      DelTree(LogsDir, True, True, True);
    
    // Удаление файла базы данных
    if FileExists(DbFile) then
      DeleteFile(DbFile);
  end;
end;
"""
    
    # Заменяем плейсхолдеры
    content = template.replace("VERSION", __version__).replace("APP_ID", app_id)
    
    # Записываем файл
    with open('setup.iss', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Файл setup.iss успешно создан для версии {__version__}")
    print(f"AppId: {app_id}")

if __name__ == "__main__":
    generate_setup_iss()
