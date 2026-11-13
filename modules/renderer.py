"""
报告渲染器 - 生成架构图和分析报告
"""
from pathlib import Path
from datetime import datetime
import json


class ReportRenderer:
    """报告渲染引擎"""
    
    def __init__(self):
        self.output_dir = Path(__file__).parent.parent / 'outputs'
        self.reports_dir = self.output_dir / 'reports'
        self.diagrams_dir = self.output_dir / 'diagrams'
        
        for d in [self.reports_dir, self.diagrams_dir]:
            d.mkdir(parents=True, exist_ok=True)
    
    def render_generate_report(self, result):
        """渲染架构生成报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        filename = f'架构方案_{timestamp}.txt'
        filepath = self.reports_dir / filename
        
        content = self._format_generate_report(result)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filepath
    
    def render_audit_report(self, result):
        """渲染架构审核报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        filename = f'审核报告_{timestamp}.txt'
        filepath = self.reports_dir / filename
        
        content = self._format_audit_report(result)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filepath
    
    def render_diagram(self, architecture):
        """渲染架构图（文本版）"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        filename = f'架构图_{timestamp}.txt'
        filepath = self.diagrams_dir / filename
        
        content = self._draw_architecture(architecture)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filepath
    
    def _format_generate_report(self, result):
        """格式化生成报告"""
        arch = result.get('architecture', {})
        recs = result.get('recommendations', [])
        steps = result.get('implementation_steps', [])
        
        report = []
        report.append('=' * 80)
        report.append('投融资股权架构方案')
        report.append(f'生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        report.append('=' * 80)
        report.append('')
        
        # 1. 推荐架构
        report.append('一、推荐架构')
        report.append('-' * 80)
        template = arch.get('template', {})
        report.append(f"架构类型: {template.get('name', '')}")
        report.append(f"适用原因: {template.get('reason', '')}")
        report.append('')
        
        # 2. 股权结构
        report.append('二、股权结构')
        report.append('-' * 80)
        equity = arch.get('equity_structure', {})
        for sh in equity.get('post_money', []):
            report.append(f"  {sh['name']}: {sh['ratio']*100:.1f}% ({sh['type']})")
        report.append('')
        
        # 3. 控制权方案
        report.append('三、控制权保护')
        report.append('-' * 80)
        control = arch.get('control_scheme', {})
        report.append(f"创始人合计持股: {control.get('founder_ratio', 0)*100:.1f}%")
        report.append(f"控制权水平: {control.get('control_level', '')}")
        for method in control.get('methods', []):
            report.append(f"  • {method['method']}: {method['description']}")
        report.append('')
        
        # 4. 税务筹划
        report.append('四、税务筹划建议')
        report.append('-' * 80)
        tax = arch.get('tax_optimization', {})
        for key, value in tax.items():
            report.append(f"{key}:")
            report.append(f"  建议: {value.get('recommendation', '')}")
            report.append(f"  收益: {value.get('benefit', '')}")
        report.append('')
        
        # 5. 实施路径
        report.append('五、实施路径（{} 步）'.format(len(steps)))
        report.append('-' * 80)
        for step in steps:
            report.append(f"第{step['step']}步: {step['action']}")
            report.append(f"  时间: {step['timeline']} | 成本: {step['cost']}")
            for detail in step.get('details', []):
                report.append(f"    - {detail}")
            report.append('')
        
        # 6. 综合建议
        if recs:
            report.append('六、综合建议')
            report.append('-' * 80)
            for rec in recs:
                report.append(f"[{rec['priority']}] {rec['category']}")
                report.append(f"  问题: {rec['issue']}")
                report.append(f"  建议: {rec['recommendation']}")
                report.append('')
        
        report.append('=' * 80)
        report.append('报告结束')
        report.append('=' * 80)
        
        return '\n'.join(report)
    
    def _format_audit_report(self, result):
        """格式化审核报告"""
        analysis = result.get('analysis', {})
        risks = result.get('risks', {})
        opts = result.get('optimizations', {})
        
        report = []
        report.append('=' * 80)
        report.append('股权架构审核报告')
        report.append(f'审核时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        report.append('=' * 80)
        report.append('')
        
        if analysis.get('demo_mode'):
            report.append('⚠️ 演示模式：当前版本未解析上传文件，以下结论基于内置示例数据，')
            report.append('   仅演示分析流程，不构成对您实际架构的审核意见。')
            report.append('')
        
        # 综合评分
        score = analysis.get('overall_score', 0)
        report.append(f'综合评分: {score}/100')
        if score >= 80:
            report.append('评级: 优秀 ✅')
        elif score >= 60:
            report.append('评级: 良好 ⚠️')
        else:
            report.append('评级: 需整改 🔴')
        report.append('')
        
        # 风险清单
        report.append('一、风险扫描结果')
        report.append('-' * 80)
        
        p0_count = len(risks.get('P0', []))
        p1_count = len(risks.get('P1', []))
        p2_count = len(risks.get('P2', []))
        
        report.append(f'P0（阻断性风险）: {p0_count}项')
        for risk in risks.get('P0', []):
            report.append(f'  🔴 {risk["category"]}: {risk["issue"]}')
            report.append(f'     解决方案: {risk["solution"]}')
        report.append('')
        
        report.append(f'P1（重大风险）: {p1_count}项')
        for risk in risks.get('P1', []):
            report.append(f'  ⚠️  {risk["category"]}: {risk["issue"]}')
            report.append(f'     解决方案: {risk["solution"]}')
        report.append('')
        
        report.append(f'P2（优化建议）: {p2_count}项')
        for risk in risks.get('P2', [])[:5]:  # 只显示前5项
            report.append(f'  💡 {risk["category"]}: {risk["issue"]}')
        report.append('')
        
        # 优化方案
        report.append('二、优化方案')
        report.append('-' * 80)
        for plan in opts.get('optimization_plans', []):
            report.append(f"{plan['title']} ({plan['plan_id']})")
            report.append(f"  现状: {plan['current_status']}")
            report.append(f"  目标: {plan['target']}")
            report.append(f"  时间: {plan['timeline']} | 成本: {plan['cost']}")
            report.append(f"  收益: {plan['benefit']}")
            report.append('')
        
        # 整改时间表
        report.append('三、整改时间表')
        report.append('-' * 80)
        total_timeline = '预计6个月完成全部整改'
        report.append(total_timeline)
        report.append('')
        
        report.append('=' * 80)
        report.append('报告结束')
        report.append('=' * 80)
        
        return '\n'.join(report)
    
    def _draw_architecture(self, architecture):
        """绘制架构图（ASCII）— 兼容生成器与审核器两种架构形态"""
        diagram = []
        diagram.append('股权架构图')
        diagram.append('=' * 60)
        diagram.append('')
        
        # 审核器形态: {type, shareholders}；生成器形态: {template, equity_structure}
        if 'equity_structure' in architecture:
            arch_type = architecture.get('template', {}).get('architecture_type', '')
            shareholders = architecture.get('equity_structure', {}).get('post_money', [])
        else:
            arch_type = architecture.get('type', '')
            shareholders = architecture.get('shareholders', [])
        
        diagram.append(f'架构类型: {arch_type}')
        diagram.append('')
        diagram.append('股东结构:')
        diagram.append('')
        
        for sh in shareholders:
            name = sh.get('name', '')
            ratio = sh.get('ratio', 0)
            
            bar_length = int(ratio * 50)
            bar = '█' * bar_length
            
            diagram.append(f'{name:20s} {ratio*100:5.1f}% │{bar}')
        
        diagram.append('')
        diagram.append('=' * 60)
        
        return '\n'.join(diagram)
