@echo off
echo ==========================================
echo 投融资股权架构智能体
echo ==========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.12+
    pause
    exit /b 1
)

echo 初始化数据库...
python scripts\init_db.py

echo.
echo 启动服务...
echo 访问地址: http://127.0.0.1:5299
echo 按 Ctrl+C 停止服务
echo.
python app.py

pause
