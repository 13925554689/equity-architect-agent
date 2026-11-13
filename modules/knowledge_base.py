"""
知识库模块 - 法规/案例/模板检索
"""
import json
import sqlite3
from pathlib import Path
import jieba


class KnowledgeBase:
    """投融资架构知识库"""
    
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = Path(__file__).parent.parent / 'data' / 'equity_architect.db'
        
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        self._load_knowledge()
    
    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 法规表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS regulations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                regulation_id TEXT UNIQUE,
                title TEXT,
                category TEXT,
                effective_date TEXT,
                content TEXT,
                keywords TEXT
            )
        ''')
        
        # 案例表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT UNIQUE,
                company TEXT,
                architecture_type TEXT,
                highlights TEXT,
                structure TEXT,
                lessons TEXT,
                keywords TEXT
            )
        ''')
        
        # 模板表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id TEXT UNIQUE,
                name TEXT,
                architecture_type TEXT,
                applicable_scenarios TEXT,
                structure TEXT,
                pros TEXT,
                cons TEXT,
                compliance_checklist TEXT
            )
        ''')
        
        # FTS5 索引表（预留，当前检索走 LIKE，jieba 中文分词对 FTS5 unicode61 收益有限）
        
        conn.commit()
        conn.close()
    
    def _load_knowledge(self):
        """加载知识库内容"""
        kb_dir = Path(__file__).parent.parent / 'knowledge_base'
        
        # 加载法规
        self._load_regulations(kb_dir / 'regulations')
        
        # 加载案例
        self._load_cases(kb_dir / 'cases')
        
        # 加载模板
        self._load_templates(kb_dir / 'templates')
    
    def _load_regulations(self, regulations_dir):
        """加载法规库"""
        if not regulations_dir.exists():
            regulations_dir.mkdir(parents=True, exist_ok=True)
            # 创建示例法规
            self._create_sample_regulation(regulations_dir)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for json_file in regulations_dir.glob('*.json'):
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                cursor.execute('''
                    INSERT OR REPLACE INTO regulations 
                    (regulation_id, title, category, effective_date, content, keywords)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    data['regulation_id'],
                    data['title'],
                    data.get('category', ''),
                    data.get('effective_date', ''),
                    json.dumps(data, ensure_ascii=False),
                    ','.join(data.get('keywords', []))
                ))
        
        conn.commit()
        conn.close()
    
    def _load_cases(self, cases_dir):
        """加载案例库"""
        if not cases_dir.exists():
            cases_dir.mkdir(parents=True, exist_ok=True)
            self._create_sample_case(cases_dir)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for json_file in cases_dir.glob('*.json'):
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                cursor.execute('''
                    INSERT OR REPLACE INTO cases 
                    (case_id, company, architecture_type, highlights, structure, lessons, keywords)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    data['case_id'],
                    data['company'],
                    data['architecture_type'],
                    json.dumps(data.get('highlights', []), ensure_ascii=False),
                    json.dumps(data.get('structure', {}), ensure_ascii=False),
                    json.dumps(data.get('lessons', []), ensure_ascii=False),
                    ','.join(data.get('keywords', []))
                ))
        
        conn.commit()
        conn.close()
    
    def _load_templates(self, templates_dir):
        """加载模板库"""
        if not templates_dir.exists():
            templates_dir.mkdir(parents=True, exist_ok=True)
            self._create_sample_template(templates_dir)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for json_file in templates_dir.glob('*.json'):
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                cursor.execute('''
                    INSERT OR REPLACE INTO templates 
                    (template_id, name, architecture_type, applicable_scenarios, 
                     structure, pros, cons, compliance_checklist)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    data['template_id'],
                    data['name'],
                    data['architecture_type'],
                    json.dumps(data.get('applicable_scenarios', []), ensure_ascii=False),
                    json.dumps(data.get('structure', {}), ensure_ascii=False),
                    json.dumps(data.get('pros', []), ensure_ascii=False),
                    json.dumps(data.get('cons', []), ensure_ascii=False),
                    json.dumps(data.get('compliance_checklist', []), ensure_ascii=False)
                ))
        
        conn.commit()
        conn.close()
    
    def search(self, query, limit=10):
        """全文检索"""
        # jieba分词
        keywords = jieba.lcut(query)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        results = []
        
        # 检索法规
        cursor.execute('''
            SELECT regulation_id, title, content 
            FROM regulations 
            WHERE keywords LIKE ? OR title LIKE ?
            LIMIT ?
        ''', (f'%{query}%', f'%{query}%', limit))
        
        for row in cursor.fetchall():
            results.append({
                'type': 'regulation',
                'id': row[0],
                'title': row[1],
                'content': json.loads(row[2])
            })
        
        # 检索案例
        cursor.execute('''
            SELECT case_id, company, architecture_type, structure
            FROM cases 
            WHERE keywords LIKE ? OR company LIKE ?
            LIMIT ?
        ''', (f'%{query}%', f'%{query}%', limit))
        
        for row in cursor.fetchall():
            results.append({
                'type': 'case',
                'id': row[0],
                'company': row[1],
                'architecture_type': row[2],
                'structure': json.loads(row[3])
            })
        
        # 检索模板
        cursor.execute('''
            SELECT template_id, name, architecture_type, structure
            FROM templates 
            WHERE name LIKE ?
            LIMIT ?
        ''', (f'%{query}%', limit))
        
        for row in cursor.fetchall():
            results.append({
                'type': 'template',
                'id': row[0],
                'name': row[1],
                'architecture_type': row[2],
                'structure': json.loads(row[3])
            })
        
        conn.close()
        return results
    
    def get_template(self, template_id):
        """获取架构模板"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM templates WHERE template_id = ?', (template_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'template_id': row[1],
                'name': row[2],
                'architecture_type': row[3],
                'applicable_scenarios': json.loads(row[4]),
                'structure': json.loads(row[5]),
                'pros': json.loads(row[6]),
                'cons': json.loads(row[7]),
                'compliance_checklist': json.loads(row[8])
            }
        return None
    
    def count_regulations(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM regulations')
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def count_cases(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM cases')
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def count_templates(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM templates')
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def _create_sample_regulation(self, regulations_dir):
        """创建示例法规"""
        sample = {
            "regulation_id": "jiuminiyao_2019",
            "title": "《全国法院民商事审判工作会议纪要》（九民纪要）",
            "category": "对赌协议",
            "effective_date": "2019-11-08",
            "keywords": ["对赌协议", "估值调整", "股权回购", "资本维持"],
            "key_points": [
                "投资方与目标公司股东对赌有效",
                "投资方与目标公司对赌需履行减资程序",
                "既要鼓励投资，又要贯彻资本维持原则"
            ]
        }
        
        with open(regulations_dir / 'jiuminiyao.json', 'w', encoding='utf-8') as f:
            json.dump(sample, f, ensure_ascii=False, indent=2)
    
    def _create_sample_case(self, cases_dir):
        """创建示例案例"""
        sample = {
            "case_id": "deepseek_2025",
            "company": "DeepSeek（杭州深度求索）",
            "architecture_type": "多层持股平台",
            "keywords": ["有限合伙", "控制权", "激励池"],
            "highlights": [
                "创始人通过3层持股平台控制",
                "有限合伙GP+LP分离",
                "预留20%激励池"
            ],
            "structure": {
                "layer1": "梁文锋（自然人）",
                "layer2": "宁波程普（有限合伙）",
                "layer3": "杭州深度求索"
            },
            "lessons": [
                "创始人不必直接担任高管",
                "多平台分散持有激励池",
                "有限合伙GP权利设计"
            ]
        }
        
        with open(cases_dir / 'deepseek.json', 'w', encoding='utf-8') as f:
            json.dump(sample, f, ensure_ascii=False, indent=2)
    
    def _create_sample_template(self, templates_dir):
        """创建示例模板"""
        sample = {
            "template_id": "startup_basic",
            "name": "创业公司基础架构",
            "architecture_type": "有限合伙持股平台",
            "applicable_scenarios": [
                "创业初期",
                "3-5位创始人",
                "计划3年内融资"
            ],
            "structure": {
                "持股平台": "有限合伙企业（创始人任GP）",
                "目标公司": "有限责任公司",
                "激励池": "15%（通过持股平台代持）"
            },
            "pros": [
                "控制权集中",
                "税务优化",
                "融资便利"
            ],
            "cons": [
                "初期设立成本",
                "需要熟悉合伙企业运作"
            ],
            "compliance_checklist": [
                "工商登记",
                "税务备案",
                "合伙协议签署"
            ]
        }
        
        with open(templates_dir / 'startup_basic.json', 'w', encoding='utf-8') as f:
            json.dump(sample, f, ensure_ascii=False, indent=2)
