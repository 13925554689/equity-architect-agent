"""
投融资股权架构智能体 - Flask 主应用
一句话口令驱动：生成架构 / 审核架构
"""
from flask import Flask, render_template, request, jsonify, send_file
from pathlib import Path
import json
from datetime import datetime

from modules.analyzer import ArchitectureAnalyzer
from modules.generator import ArchitectureGenerator
from modules.risk_scanner import RiskScanner
from modules.optimizer import ArchitectureOptimizer
from modules.renderer import ReportRenderer
from modules.knowledge_base import KnowledgeBase

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB
app.config['UPLOAD_FOLDER'] = Path(__file__).parent / 'uploads'
app.config['OUTPUT_FOLDER'] = Path(__file__).parent / 'outputs'

# 初始化核心模块
kb = KnowledgeBase()
analyzer = ArchitectureAnalyzer(kb)
generator = ArchitectureGenerator(kb)
scanner = RiskScanner(kb)
optimizer = ArchitectureOptimizer(kb)
renderer = ReportRenderer()

# 确保目录存在
for folder in ['uploads', 'outputs', 'outputs/reports', 'outputs/diagrams']:
    (Path(__file__).parent / folder).mkdir(parents=True, exist_ok=True)


@app.after_request
def security_headers(resp):
    """一行件: 基础安全响应头（评审 P2，防嵌套/嗅探）"""
    resp.headers.setdefault('X-Content-Type-Options', 'nosniff')
    resp.headers.setdefault('X-Frame-Options', 'DENY')
    resp.headers.setdefault('Referrer-Policy', 'no-referrer')
    return resp


@app.route('/')
def index():
    """首页 - 口令入口"""
    return render_template('index.html')


@app.route('/command', methods=['POST'])
def handle_command():
    """处理口令：生成架构 / 审核架构"""
    data = request.get_json()
    command = data.get('command', '').strip()
    
    if '生成' in command or 'generate' in command.lower():
        return jsonify({
            'action': 'generate',
            'redirect': '/generate'
        })
    elif '审核' in command or 'audit' in command.lower():
        return jsonify({
            'action': 'audit',
            'redirect': '/audit'
        })
    else:
        return jsonify({
            'error': '未识别的口令，请输入：生成架构 或 审核架构'
        }), 400


@app.route('/generate')
def generate_page():
    """架构生成页面"""
    return render_template('generate.html')


@app.route('/audit')
def audit_page():
    """架构审核页面"""
    return render_template('audit.html')


@app.route('/api/generate', methods=['POST'])
def api_generate():
    """API: 生成架构方案"""
    try:
        data = request.get_json()
        
        # 1. 生成架构方案
        result = generator.generate(data)
        
        # 2. 风险扫描
        risks = scanner.scan(result['architecture'])
        result['risks'] = risks
        
        # 3. 生成报告
        report_path = renderer.render_generate_report(result)
        
        # 4. 生成架构图
        diagram_path = renderer.render_diagram(result['architecture'])
        
        return jsonify({
            'success': True,
            'architecture': result['architecture'],
            'recommendations': result['recommendations'],
            'risks': risks,
            'report_url': f'/download/{report_path.name}',
            'diagram_url': f'/download/{diagram_path.name}'
        })
    except ValueError as e:
        # 输入错误（如股东结构缺失）→ 400 带原因，不是服务器错误
        return jsonify({'error': str(e)}), 400
    except Exception:
        import logging
        logging.exception('请求处理失败')
        return jsonify({'error': '服务器内部错误，请检查输入或查看日志'}), 500


@app.route('/api/audit', methods=['POST'])
def api_audit():
    """API: 审核架构"""
    try:
        # 处理上传文件
        files = request.files.getlist('files')
        materials = []
        
        for file in files:
            if file.filename:
                # 信任边界: 剥目录成分防任意路径写入；空名兜底时间戳
                safe = Path(file.filename).name
                if not safe:
                    safe = f'upload_{datetime.now().strftime("%H%M%S%f")}.bin'
                filepath = app.config['UPLOAD_FOLDER'] / safe
                file.save(filepath)
                materials.append(str(filepath))
        
        # 1. 分析架构
        analysis = analyzer.analyze(materials)
        
        # 2. 风险扫描
        risks = scanner.scan(analysis['architecture'])
        
        # 3. 生成优化建议
        optimizations = optimizer.optimize(analysis, risks)
        
        # 4. 生成审核报告
        report_path = renderer.render_audit_report({
            'analysis': analysis,
            'risks': risks,
            'optimizations': optimizations
        })
        
        return jsonify({
            'success': True,
            'analysis': analysis,
            'risks': risks,
            'optimizations': optimizations,
            'report_url': f'/download/{report_path.name}'
        })
    except Exception:
        import logging
        logging.exception('请求处理失败')
        return jsonify({'error': '服务器内部错误，请检查输入或查看日志'}), 500


@app.route('/api/knowledge/search')
def search_knowledge():
    """知识库检索"""
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': '缺少查询参数'}), 400
    
    results = kb.search(query)
    return jsonify({'results': results})


@app.route('/download/<filename>')
def download_file(filename):
    """下载生成的报告/图表"""
    # 信任边界: pathlib 在 Windows 下 'dir / C:/x' 会整体覆盖为绝对路径（实测可读 win.ini）
    # 用 .name 剥离一切目录成分（含盘符/反斜杠/..），剥完与原名不等即拒绝
    safe = Path(filename).name
    if not safe or safe != filename:
        return '非法文件名', 400
    
    filepath = app.config['OUTPUT_FOLDER'] / safe
    if not filepath.exists():
        filepath = app.config['OUTPUT_FOLDER'] / 'reports' / safe
    if not filepath.exists():
        filepath = app.config['OUTPUT_FOLDER'] / 'diagrams' / safe
    
    if filepath.exists():
        return send_file(filepath, as_attachment=True)
    return '文件不存在', 404


@app.route('/health')
def health():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'knowledge_base': {
            'regulations': kb.count_regulations(),
            'cases': kb.count_cases(),
            'templates': kb.count_templates()
        }
    })


if __name__ == '__main__':
    import os
    print('=' * 60)
    print('投融资股权架构智能体已启动')
    print('访问地址: http://127.0.0.1:5299')
    print('口令: 生成架构 | 审核架构')
    print('=' * 60)
    # ponytail: 调试器仅在显式 FLASK_DEBUG=1 时开，且只绑本机（Werkzeug 调试器=远程代码执行面）
    app.run(host='127.0.0.1', port=5299,
            debug=os.environ.get('FLASK_DEBUG') == '1', use_reloader=False)
