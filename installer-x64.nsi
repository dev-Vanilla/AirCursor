;--------------------------------
; 安装器基本信息
;--------------------------------

Name "AirCursor"
OutFile "AirCursorInstaller-x86_64.exe"
InstallDir "$PROGRAMFILES\AirCursor"
Icon "./resources/imgs/icon.ico"        ; 设置应用图标
ShowInstDetails show
ShowUnInstDetails hide

;--------------------------------
; 引入库
;--------------------------------

!include LogicLib.nsh         ; 用于条件语句
!include nsDialogs.nsh        ; 用于自定义页面

;--------------------------------
; 页面定义
;--------------------------------

Page components
Page directory
Page instfiles
Page custom ShowFinishedPage

;--------------------------------
; 组件部分 - 主程序
;--------------------------------

Section "Main Application" SEC01

  SetOutPath "$INSTDIR"

  ; 拷贝主程序
  File "AirCursor-x64.exe"

  ; 创建开始菜单快捷方式
  CreateDirectory "$STARTMENU\AirCursor"
  CreateShortcut "$STARTMENU\AirCursor\AirCursor.lnk" "$INSTDIR\AirCursor.exe"

SectionEnd

;--------------------------------
; 可选组件 - 创建桌面快捷方式
;--------------------------------

Section "Create Desktop Shortcut" SEC_DESKTOP

  CreateShortcut "$DESKTOP\AirCursor.lnk" "$INSTDIR\AirCursor.exe"

SectionEnd

;--------------------------------
; Finished 页面 - 安装完成后显示提示
;--------------------------------

Function ShowFinishedPage
  nsDialogs::Create 1018
  Pop $0

  ${If} $0 == error
    Abort
  ${EndIf}

  ; 显示提示信息
  ${NSD_CreateLabel} 0 0 100% 12u "AirCursor has been successfully installed."
  Pop $0

  nsDialogs::Show
FunctionEnd
