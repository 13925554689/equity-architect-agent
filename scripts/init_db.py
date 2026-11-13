"""
初始化数据库脚本
"""
from pathlib import Path
import sys

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.knowledge_base import KnowledgeBase

if __name__ == '__main__':
    print('初始化投融资架构智能体数据库...')
    
    kb = KnowledgeBase()
    
    print(f'✅ 数据库初始化完成')
    print(f'   法规数量: {kb.count_regulations()}')
    print(f'   案例数量: {kb.count_cases()}')
    print(f'   模板数量: {kb.count_templates()}')
    print('')
    print('可以启动应用了: python app.py')
