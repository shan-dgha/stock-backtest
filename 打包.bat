@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ==========================================
echo  正在打包，请等待 3~5 分钟，不要关闭窗口
echo ==========================================
".venv\Scripts\python.exe" -m PyInstaller --noconfirm --windowed --name DataDashboard app.py
echo.
if exist "dist\DataDashboard\DataDashboard.exe" (
    echo [成功] 产物: dist\DataDashboard\DataDashboard.exe
    echo 发人时请压缩整个 dist\DataDashboard 文件夹
) else (
    echo [失败] 没生成 exe，把上面的报错贴出来
)
pause