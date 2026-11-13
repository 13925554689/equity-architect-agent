# 投融资股权架构智能体 - 快速启动脚本

echo "=========================================="
echo "投融资股权架构智能体"
echo "=========================================="
echo ""

# 检查Python
python --version
if [ $? -ne 0 ]; then
    echo "错误: 未找到Python，请先安装Python 3.12+"
    exit 1
fi

# 初始化数据库
echo "初始化数据库..."
python scripts/init_db.py

# 启动服务
echo ""
echo "启动服务..."
echo "访问地址: http://localhost:5299"
echo "按 Ctrl+C 停止服务"
echo ""
python app.py
