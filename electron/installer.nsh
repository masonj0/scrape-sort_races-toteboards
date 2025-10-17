; electron/installer.nsh
; NSIS include script for running dependency installation after file copy.

!macro customInstall
  ; This is where we run our dependency installer
  DetailPrint "Running post-installation setup (Python & Node.js dependencies)..."
  ; We execute the bundled node to run our script
  nsExec::ExecToLog '"$INSTDIR\resources\app\electron\install-dependencies.js"'
!macroend