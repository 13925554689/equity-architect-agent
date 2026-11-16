"""
架构分析引擎 - 全面分析现有股权架构
"""
import json
from pathlib import Path


class ArchitectureAnalyzer:
    """投融资架构分析引擎"""
    
    def __init__(self, knowledge_base):
        self.kb = knowledge_base
    
    def analyze(self, materials):
        """
        分析现有架构
        
        Args:
            materials: 上传的材料文件路径列表
        
        Returns:
            {
                'architecture': {...},
                'control_analysis': {...},
                'financing_history': {...},
                'compliance': {...}
            }
        """
        # 解析材料
        parsed_data = self._parse_materials(materials)
        
        # 1. 架构识别
        architecture = self._identify_architecture(parsed_data)
        
        # 2. 控制权分析
        control_analysis = self._analyze_control(architecture)
        
        # 3. 融资历史合规性
        financing_compliance = self._analyze_financing(parsed_data)
        
        # 4. 员工激励分析
        incentive_analysis = self._analyze_incentive(parsed_data)
        
        # 5. 税务分析
        tax_analysis = self._analyze_tax(architecture)
        
        # 6. 上市合规性
        ipo_compliance = self._analyze_ipo_compliance(architecture, parsed_data)
        
        return {
            'architecture': architecture,
            'demo_mode': parsed_data.get('demo_mode', False),
            'control_analysis': control_analysis,
            'financing_compliance': financing_compliance,
            'incentive_analysis': incentive_analysis,
            'tax_analysis': tax_analysis,
            'ipo_compliance': ipo_compliance,
            'overall_score': self._calculate_score(
                control_analysis, 
                financing_compliance, 
                incentive_analysis, 
                tax_analysis, 
                ipo_compliance
            )
        }
    
    def _parse_materials(self, materials):
        """解析上传的材料
        
        ponytail: MVP 未接 PDF/Word 解析，返回内置示例数据演示流程；
        结果标注 demo_mode=True，报告会显式声明，勿当作对真实文件的结论。
        接入解析器（pymupdf/python-docx）后替换本函数即可。
        """
        return {
            'demo_mode': True,
            'shareholders': [
                {'name': '创始人A', 'ratio': 0.35, 'type': 'founder'},
                {'name': '创始人B', 'ratio': 0.15, 'type': 'founder'},
                {'name': 'A轮投资人', 'ratio': 0.20, 'type': 'investor'},
                {'name': 'B轮投资人', 'ratio': 0.20, 'type': 'investor'},
                {'name': '员工持股平台', 'ratio': 0.10, 'type': 'option_pool'}
            ],
            'financing_rounds': [
                {'round': 'A轮', 'amount': 10000000, 'valuation': 50000000, 'date': '2023-06'},
                {'round': 'B轮', 'amount': 30000000, 'valuation': 150000000, 'date': '2024-09'}
            ]
        }
    
    def _identify_architecture(self, parsed_data):
        """识别架构类型"""
        shareholders = parsed_data.get('shareholders', [])
        
        # 检查是否有持股平台
        has_platform = any('持股平台' in sh['name'] for sh in shareholders)
        
        # 检查是否有境外主体
        has_offshore = False  # 简化版
        
        if has_offshore:
            architecture_type = 'VIE' if '协议控制' in str(parsed_data) else '红筹'
        elif has_platform:
            architecture_type = '有限合伙持股平台'
        else:
            architecture_type = '直接持股'
        
        return {
            'type': architecture_type,
            'shareholders': shareholders,
            'layers': 2 if has_platform else 1
        }
    
    def _analyze_control(self, architecture):
        """控制权分析"""
        shareholders = architecture.get('shareholders', [])
        
        founder_ratio = sum([sh['ratio'] for sh in shareholders if sh['type'] == 'founder'])
        investor_ratio = sum([sh['ratio'] for sh in shareholders if sh['type'] == 'investor'])
        
        # 判断控制权水平
        if founder_ratio >= 0.67:
            control_level = 'strong'
            control_desc = '绝对控制（≥67%）'
        elif founder_ratio >= 0.51:
            control_level = 'medium'
            control_desc = '相对控制（≥51%）'
        elif founder_ratio >= 0.34:
            control_level = 'weak'
            control_desc = '一票否决（≥34%）'
        else:
            control_level = 'at_risk'
            control_desc = '控制权不足（<34%）'
        
        return {
            'founder_ratio': founder_ratio,
            'investor_ratio': investor_ratio,
            'control_level': control_level,
            'control_desc': control_desc,
            'status': '✅' if founder_ratio >= 0.34 else '🔴',
            'recommendations': [] if founder_ratio >= 0.34 else [
                '建议签署一致行动人协议',
                '章程约定重大事项特别表决',
                '投资人委托投票权'
            ]
        }
    
    def _analyze_financing(self, parsed_data):
        """融资历史合规性分析"""
        rounds = parsed_data.get('financing_rounds', [])
        
        issues = []
        
        for round_data in rounds:
            # 检查对赌协议（模拟）
            if round_data['round'] == 'A轮':
                issues.append({
                    'round': 'A轮',
                    'priority': 'P0',
                    'issue': '对赌协议约定目标公司回购，未履行减资程序',
                    'risk': '投资人诉讼风险，影响上市',
                    'solution': '与投资人协商修改对赌主体为创始人'
                })
            
            if round_data['round'] == 'B轮':
                issues.append({
                    'round': 'B轮',
                    'priority': 'P1',
                    'issue': '未办理递延纳税备案（员工激励部分）',
                    'risk': '员工税负增加（45% vs 20%）',
                    'solution': '补办101号文备案'
                })
        
        return {
            'rounds': rounds,
            'issues': issues,
            'compliance_rate': 1 - len(issues) / max(len(rounds), 1)
        }
    
    def _analyze_incentive(self, parsed_data):
        """员工激励分析"""
        shareholders = parsed_data.get('shareholders', [])
        
        option_pool_ratio = sum([sh['ratio'] for sh in shareholders if sh['type'] == 'option_pool'])
        
        status = '✅' if option_pool_ratio >= 0.10 else '⚠️'
        
        return {
            'option_pool_ratio': option_pool_ratio,
            'status': status,
            'evaluation': 'adequate' if option_pool_ratio >= 0.15 else 'insufficient',
            'recommendation': '建议增加至15-20%' if option_pool_ratio < 0.15 else '期权池充足'
        }
    
    def _analyze_tax(self, architecture):
        """税务分析"""
        return {
            '持股平台注册地': {
                'current': '北京',
                'status': '⚠️',
                'issue': '无税收优惠',
                'recommendation': '建议迁址至宁波等税收洼地（已过时：权益性投资的独资合伙企业一律查账征收，财政部 税务总局公告2021年第41号）',
                'estimated_saving': '洼地套利不再计入筹划收益，财政返还不可持续且有追溯风险'
            },
            '递延纳税备案': {
                'status': '⚠️',
                'issue': '未办理101号文备案',
                'recommendation': '补办递延纳税备案'
            }
        }
    
    def _analyze_ipo_compliance(self, architecture, parsed_data):
        """上市合规性分析"""
        issues = []
        
        # 代持检查
        issues.append({
            'category': '股权清晰',
            'priority': 'P0',
            'issue': '存在2名员工代持未显名',
            'solution': '显名登记至持股平台'
        })
        
        # 控制权稳定性
        issues.append({
            'category': '实际控制人',
            'priority': 'P1',
            'issue': '需律所出具实际控制人认定文件',
            'solution': '委托律所出具法律意见'
        })
        
        return {
            'target': '科创板',
            'issues': issues,
            'estimated_timeline': '6个月整改',
            'readiness': 'medium'
        }
    
    def _calculate_score(self, control, financing, incentive, tax, ipo):
        """计算综合评分"""
        scores = []
        
        # 控制权（30分）
        if control['control_level'] == 'strong':
            scores.append(30)
        elif control['control_level'] == 'medium':
            scores.append(22)
        elif control['control_level'] == 'weak':
            scores.append(15)
        else:
            scores.append(5)
        
        # 融资合规（25分）
        scores.append(25 * financing['compliance_rate'])
        
        # 激励方案（20分）
        if incentive['option_pool_ratio'] >= 0.15:
            scores.append(20)
        elif incentive['option_pool_ratio'] >= 0.10:
            scores.append(15)
        else:
            scores.append(8)
        
        # 税务优化（15分）
        scores.append(7)  # 简化评分
        
        # 上市合规（10分）
        if ipo['readiness'] == 'high':
            scores.append(10)
        elif ipo['readiness'] == 'medium':
            scores.append(6)
        else:
            scores.append(3)
        
        return int(sum(scores))
