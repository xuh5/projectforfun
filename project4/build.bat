@echo off
echo ========================================
echo   TextTool 打包工具
echo ========================================
echo.

REM 激活虚拟环境
call venv\Scripts\activate

REM 安装 pyinstaller（如果没有的话）
pip install pyinstaller

REM 打包
echo.
echo [打包中...] 请稍候
echo.
pyinstaller build.spec --clean

echo.
echo ========================================
echo   打包完成！
echo   输出位置: dist\TextTool.exe
echo ========================================
pause
