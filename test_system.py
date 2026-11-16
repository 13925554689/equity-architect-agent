"""
快速验证脚本 - 测试所有核心模块
"""
import sys
import json
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """测试模块导入"""
    print('1️⃣ 测试模块导入...')
    try:
        from modules.knowledge_base import KnowledgeBase
        from modules.generator import ArchitectureGenerator
        from modules.analyzer import ArchitectureAnalyzer
        from modules.risk_scanner import RiskScanner
        from modules.optimizer import ArchitectureOptimizer
        from modules.renderer import ReportRenderer
        print('   ✅ 所有模块导入成功')
        return True
    except Exception as e:
        print(f'   ❌ 模块导入失败: {e}')
        return False

def test_knowledge_base():
    """测试知识库"""
    print('\n2️⃣ 测试知识库...')
    try:
        from modules.knowledge_base import KnowledgeBase
        kb = KnowledgeBase()
        
        reg_count = kb.count_regulations()
        case_count = kb.count_cases()
        template_count = kb.count_templates()
        
        print(f'   ✅ 法规: {reg_count}条')
        print(f'   ✅ 案例: {case_count}个')
        print(f'   ✅ 模板: {template_count}套')
        
        # 测试检索
        results = kb.search('对赌协议')
        print(f'   ✅ 检索测试: 找到{len(results)}条结果')
        
        # 三层架构文章融合知识：两法规+一模板必须可检索
        hits = {r['id'] for r in kb.search('人格混同') if r['type'] == 'regulation'}
        assert 'company_law_art23_2023' in hits, '人格混同检索未命中公司法23条'
        hits = {r['id'] for r in kb.search('保本保收益') if r['type'] == 'regulation'}
        assert 'fundraising_redline_2021' in hits, '保本保收益检索未命中非法集资红线'
        # 内容完整性：检索命中条目的 key_points 不得为空（评审P1：只验id不验内容）
        for q, rid in [('人格混同', 'company_law_art23_2023'), ('保本保收益', 'fundraising_redline_2021')]:
            cont = next(r['content'] for r in kb.search(q) if r.get('id') == rid)
            assert len(cont.get('key_points', [])) >= 3, f'{rid} key_points 疑似被清空'
        hits = {r['id'] for r in kb.search('三层持股') if r['type'] == 'template'}
        assert 'wallet_three_layer' in hits, '三层持股检索未命中钱包三层模板'
        # architecture_type 维度也可检索（评审P1：模板搜索只查name）
        assert any(r['id'] == 'wallet_three_layer' for r in kb.search('钱包公司三层架构')), \
            '按architecture_type检索未命中'
        tpl = kb.get_template('wallet_three_layer')
        assert tpl and '国税函〔2001〕84号' in ''.join(tpl['cons']), '模板税务修正注释缺失'
        assert tpl['pros'] and tpl['compliance_checklist'], '模板pros/checklist为空'
        # 负例：不存在的关键词与空串不抛异常（评审P1：无负例覆盖）
        assert kb.search('不存在关键词xyzq') == [], '负例检索应返回空列表'
        assert isinstance(kb.search(''), list), '空串检索不应抛异常'
        print(f'   ✅ 融合知识检索: 人格混同/保本保收益/三层持股 全部命中（含负例与内容完整性）')
        
        return True
    except Exception as e:
        print(f'   ❌ 知识库测试失败: {e}')
        return False

def test_generator():
    """测试生成引擎"""
    print('\n3️⃣ 测试架构生成引擎...')
    try:
        from modules.knowledge_base import KnowledgeBase
        from modules.generator import ArchitectureGenerator
        
        kb = KnowledgeBase()
        generator = ArchitectureGenerator(kb)
        
        # 模拟生成请求
        requirements = {
            'company': {
                'name': '测试公司',
                'registered_capital': 5000000,
                'industry': '互联网',
                'shareholders': [
                    {'name': '张三', 'ratio': 0.55},
                    {'name': '李四', 'ratio': 0.30},
                    {'name': '王五', 'ratio': 0.15}
                ]
            },
            'financing': {
                'amount': 30000000,
                'valuation': 200000000
            },
            'ipo_plan': {
                'target': '科创板'
            }
        }
        
        result = generator.generate(requirements)
        
        # 真断言（评审P2-08: 打印即通过的假绿）
        post = result['architecture']['equity_structure']['post_money']
        total = sum(s['ratio'] for s in post)
        assert abs(total - 1.0) < 1e-6, f'股权合计={total}≠100%'
        founders = sum(s['ratio'] for s in post if s['type'] == 'founder')
        assert founders > 0, '创始人比例=0'
        assert len(result.get('implementation_steps', [])) == 6
        # 税务口径修正（三层架构文章融合）: 分红路径不得再宣称平台免税/避免双重征税
        tax_opt = result['architecture']['tax_optimization']
        tax_path = tax_opt['分红路径']['recommendation']
        assert '84号' in tax_path, '分红路径应引用国税函〔2001〕84号（穿透不省税）'
        assert '避免双重征税' not in tax_path, '分红路径仍残留免税旧话术'
        assert '免税' not in tax_path, '分红路径仍宣称平台免税'
        # 全链路口径一致（评审P1：optimizer/analyzer/risk_scanner 兄弟调用点）
        assert '避免双重征税' not in json.dumps(tax_opt, ensure_ascii=False)
        
        print(f'   ✅ 生成方案成功')
        print(f'   ✅ 架构类型: {result["architecture"]["template"].get("name", "未知")}')
        print(f'   ✅ 股权合计100%，创始人{founders*100:.1f}%，实施步骤6步')
        
        return True
    except Exception as e:
        print(f'   ❌ 生成引擎测试失败: {e}')
        import traceback
        traceback.print_exc()
        return False

def test_analyzer():
    """测试分析引擎"""
    print('\n4️⃣ 测试架构分析引擎...')
    try:
        from modules.knowledge_base import KnowledgeBase
        from modules.analyzer import ArchitectureAnalyzer
        
        kb = KnowledgeBase()
        analyzer = ArchitectureAnalyzer(kb)
        
        # 模拟分析请求
        result = analyzer.analyze([])
        
        print(f'   ✅ 分析成功')
        print(f'   ✅ 综合评分: {result.get("overall_score", 0)}分')
        
        return True
    except Exception as e:
        print(f'   ❌ 分析引擎测试失败: {e}')
        import traceback
        traceback.print_exc()
        return False

def test_risk_scanner():
    """测试风险扫描器"""
    print('\n5️⃣ 测试风险扫描器...')
    try:
        from modules.knowledge_base import KnowledgeBase
        from modules.risk_scanner import RiskScanner
        
        kb = KnowledgeBase()
        scanner = RiskScanner(kb)
        
        print(f'   ✅ 风险规则库: {len(scanner.risk_rules)}条')
        
        # 模拟扫描
        test_arch = {
            'control_scheme': {'founder_ratio': 0.3},
            'equity_structure': {'option_pool': 0.05}
        }
        
        risks = scanner.scan(test_arch)
        
        # 真断言: founder_ratio=0.3 必须命中R01；形态契约归一后不再恒死
        assert len(risks.get('P0', [])) >= 1, 'founder_ratio=0.3应触发R01控制权风险'
        assert any('34%' in r['issue'] for r in risks['P0']), 'P0应含控制权一票否决线'
        
        print(f'   ✅ P0风险: {len(risks.get("P0", []))}项')
        print(f'   ✅ P1风险: {len(risks.get("P1", []))}项')
        print(f'   ✅ P2建议: {len(risks.get("P2", []))}项')
        
        return True
    except Exception as e:
        print(f'   ❌ 风险扫描器测试失败: {e}')
        import traceback
        traceback.print_exc()
        return False

def test_flask_app():
    """测试Flask应用"""
    print('\n6️⃣ 测试Flask应用...')
    try:
        import app
        
        print('   ✅ Flask应用加载成功')
        print(f'   ✅ 路由数量: {len(app.app.url_map._rules)}')
        
        return True
    except Exception as e:
        print(f'   ❌ Flask应用测试失败: {e}')
        import traceback
        traceback.print_exc()
        return False

def main():
    print('=' * 60)
    print('投融资股权架构智能体 - 系统验证')
    print('=' * 60)
    print()
    
    tests = [
        test_imports,
        test_knowledge_base,
        test_generator,
        test_analyzer,
        test_risk_scanner,
        test_flask_app
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1
    
    print()
    print('=' * 60)
    print(f'测试完成: {passed}个通过, {failed}个失败')
    print('=' * 60)
    
    if failed == 0:
        print('\n✅ 所有测试通过！系统可以正常启动。')
        print('\n启动命令: python app.py')
        print('访问地址: http://localhost:5299')
        return 0
    else:
        print(f'\n❌ 有{failed}个测试失败，请检查错误信息。')
        return 1

if __name__ == '__main__':
    sys.exit(main())
