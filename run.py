#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
投融资股权架构智能体 - 一键启动脚本
"""
import subprocess
import sys
import os
from pathlib import Path

def main():
    # 确保在项目根目录
    root = Path(__file__).parent
    os.chdir(root)
    
    # 使用项目虚拟环境
    if sys.platform == 'win32':
        python = root / '.venv' / 'Scripts' / 'python.exe'
    else:
        python = root / '.venv' / 'bin' / 'python'
    
    if not python.exists():
        print('❌ 虚拟环境不存在，请先运行: python -m venv .venv')
        print('   然后安装依赖: pip install -r requirements.txt')
        sys.exit(1)
    
    print('=' * 60)
    print('投融资股权架构智能体')
    print('=' * 60)
    print('')
    
    # 初始化数据库
    print('📦 初始化数据库...')
    result = subprocess.run([str(python), 'scripts/init_db.py'], 
                          capture_output=True, text=True, encoding='utf-8')
    if result.returncode == 0:
        print(result.stdout)
    else:
        print('❌ 数据库初始化失败')
        print(result.stderr)
        sys.exit(1)
    
    # 启动服务
    print('🚀 启动服务...')
    print('   访问地址: http://localhost:5299')
    print('   口令: 生成架构 | 审核架构')
    print('   按 Ctrl+C 停止服务')
    print('')
    
    try:
        subprocess.run([str(python), 'app.py'])
    except KeyboardInterrupt:
        print('\n\n服务已停止')

if __name__ == '__main__':
    main()
