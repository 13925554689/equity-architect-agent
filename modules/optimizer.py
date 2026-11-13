"""
优化建议引擎 - 基于分析结果给出优化方案
"""


class ArchitectureOptimizer:
    """架构优化引擎"""
    
    def __init__(self, knowledge_base):
        self.kb = knowledge_base
    
    def optimize(self, analysis, risks):
        """
        生成优化方案
        
        Returns:
            {
                'priority_fixes': [...],
                'optimization_plans': [...],
                'estimated_benefits': {...}
            }
        """
        priority_fixes = self._generate_priority_fixes(risks)
        optimization_plans = self._generate_optimization_plans(analysis)
        estimated_benefits = self._estimate_benefits(optimization_plans)
        
        return {
            'priority_fixes': priority_fixes,
            'optimization_plans': optimization_plans,
            'estimated_benefits': estimated_benefits
        }
    
    def _generate_priority_fixes(self, risks):
        """生成优先修复清单"""
        fixes = []
        
        # P0问题必须立即修复
        for risk in risks.get('P0', []):
            fixes.append({
                'priority': 'P0',
                'issue': risk['issue'],
                'action': risk['solution'],
                'timeline': '立即（1-2周）',
                'impact': '阻断性风险，影响融资/上市'
            })
        
        # P1问题建议尽快修复
        for risk in risks.get('P1', []):
            fixes.append({
                'priority': 'P1',
                'issue': risk['issue'],
                'action': risk['solution'],
                'timeline': '1个月内',
                'impact': '重大风险，影响架构质量'
            })
        
        return fixes
    
    def _generate_optimization_plans(self, analysis):
        """生成优化方案"""
        plans = []
        
        # 方案1：控制权加固
        control = analysis.get('control_analysis', {})
        if control.get('control_level') in ['weak', 'at_risk']:
            plans.append({
                'plan_id': 'OPT-001',
                'title': '控制权加固方案',
                'current_status': f"创始人持股{control.get('founder_ratio', 0)*100:.1f}%",
                'target': '确保创始人实际控制权稳定',
                'actions': [
                    '签署一致行动人协议（所有创始人）',
                    '修改章程：重大事项需创始人67%同意',
                    '投资人委托部分表决权给创始人（5年）',
                    '设立家族信托持有创始人股权'
                ],
                'timeline': '2个月',
                'cost': '律师费5-10万',
                'benefit': '控制权从"弱"提升至"中"'
            })
        
        # 方案2：税务优化
        tax = analysis.get('tax_analysis', {})
        if '⚠️' in str(tax):
            plans.append({
                'plan_id': 'OPT-002',
                'title': '税务优化方案',
                'current_status': '持股平台在北京，无税收优惠',
                'target': '降低上市后减持税负',
                'actions': [
                    '持股平台迁址至宁波（地方留存40%返还）',
                    '办理101号文递延纳税备案',
                    '优化分红路径：公司→平台（免税）→个人'
                ],
                'timeline': '1个月',
                'cost': '迁址费用1-2万',
                'benefit': '上市后减持1亿节税800万'
            })
        
        # 方案3：融资空间拓展
        plans.append({
            'plan_id': 'OPT-003',
            'title': '融资空间拓展方案',
            'current_status': '期权池10%，下轮融资空间受限',
            'target': '为C轮融资预留15%空间',
            'actions': [
                '期权池扩大至15%（老股东同比例稀释）',
                '设置可转债融资通道（不稀释股权）',
                '与现有投资人约定老股转让条款'
            ],
            'timeline': '3个月',
            'cost': '律师费3-5万',
            'benefit': '可承接5000万-1亿C轮融资'
        })
        
        return plans
    
    def _estimate_benefits(self, plans):
        """估算优化收益"""
        return {
            'tax_saving': '800万+（上市后减持1亿）',
            'control_stability': '控制权风险从高降至中',
            'financing_capacity': '可额外融资5000万-1亿',
            'ipo_readiness': '整改后6个月可申报上市',
            'total_value': '综合价值提升15-20%'
        }
