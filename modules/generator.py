"""
架构生成引擎 - 根据需求生成最优股权架构方案
"""
import json
from datetime import datetime


class ArchitectureGenerator:
    """投融资架构生成引擎"""
    
    def __init__(self, knowledge_base):
        self.kb = knowledge_base
    
    def generate(self, requirements):
        """
        根据需求生成架构方案
        
        Args:
            requirements: {
                'company': {...},
                'financing': {...},
                'ipo_plan': {...},
                'control_preference': {...}
            }
        
        Returns:
            {
                'architecture': {...},
                'recommendations': [...],
                'implementation_steps': [...]
            }
        """
        company = requirements.get('company', {})
        financing = requirements.get('financing', {})
        ipo_plan = requirements.get('ipo_plan', {})
        
        # 1. 选择基础架构模板
        template = self._select_template(company, financing, ipo_plan)
        
        # 2. 计算股权比例
        equity_structure = self._calculate_equity(company, financing, template)
        
        # 3. 设计控制权方案
        control_scheme = self._design_control(equity_structure, requirements)
        
        # 4. 税务筹划建议
        tax_optimization = self._tax_optimization(equity_structure)
        
        # 5. 对赌条款建议
        valuation_adjustment = self._valuation_adjustment_terms(financing)
        
        # 6. 实施路径
        implementation = self._implementation_steps(template, equity_structure)
        
        return {
            'architecture': {
                'template': template,
                'equity_structure': equity_structure,
                'control_scheme': control_scheme,
                'tax_optimization': tax_optimization,
                'valuation_adjustment': valuation_adjustment
            },
            'recommendations': self._generate_recommendations(equity_structure, ipo_plan),
            'implementation_steps': implementation
        }
    
    def _select_template(self, company, financing, ipo_plan):
        """选择最佳架构模板"""
        # 根据行业、规模、上市地选择
        industry = company.get('industry', '')
        ipo_target = ipo_plan.get('target', '')
        
        # 境内上市（科创板/创业板/主板）：VIE/红筹均不适用，标准架构（评审：原逻辑无视上市地把教育行业推VIE）
        if ipo_target in ['科创板', '创业板', '主板', '北交所']:
            return self.kb.get_template('startup_basic') or {
                'template_id': 'startup_basic',
                'name': '创业公司基础架构',
                'architecture_type': '有限合伙持股平台',
                'reason': f'{ipo_target}为境内上市，采用有限合伙持股平台架构'
            }
        
        # VIE架构判断（外资限制行业 + 境外上市）
        restricted_industries = ['教育', '医疗', '媒体', '互联网信息服务']
        if ipo_target in ['港股', '美股', 'HK', 'US'] and any(ind in industry for ind in restricted_industries):
            return self.kb.get_template('vie_standard') or {
                'template_id': 'vie_standard',
                'name': 'VIE协议控制架构',
                'architecture_type': 'VIE',
                'reason': '行业属于外资准入限制类别且计划境外上市'
            }
        
        # 红筹架构判断（境外上市）
        if ipo_target in ['港股', '美股', 'HK', 'US']:
            return self.kb.get_template('red_chip') or {
                'template_id': 'red_chip',
                'name': '红筹架构',
                'architecture_type': '红筹',
                'reason': '境外上市需求'
            }
        
        # 标准创业架构
        return self.kb.get_template('startup_basic') or {
            'template_id': 'startup_basic',
            'name': '创业公司基础架构',
            'architecture_type': '有限合伙持股平台',
            'reason': '标准架构'
        }
    
    def _calculate_equity(self, company, financing, template):
        """计算股权比例"""
        # 归一化与越界守卫: 比例必须>0，按和归一到100%（评审实测 2100%/-115% 源于无守卫）
        shareholders = [s for s in company.get('shareholders', []) if s.get('ratio', 0) > 0]
        total_current = sum(s.get('ratio', 0) for s in shareholders)
        if total_current <= 0:
            raise ValueError('股东结构缺失或比例非法：请提供每位创始人的持股比例（如 张三:55,李四:30,王五:15）')
        shareholders = [{**s, 'ratio': s['ratio'] / total_current} for s in shareholders]
        
        # 融资稀释
        valuation = financing.get('valuation', 0)
        amount = financing.get('amount', 0)
        dilution = amount / valuation if valuation > 0 else 0.15  # 默认15%
        
        # 期权池预留
        option_pool = financing.get('option_pool', 0.15)  # 默认15%
        
        # 稀释+期权池不得超过存量（否则创始人比例变负）
        if dilution + option_pool >= 1.0:
            dilution = min(dilution, 0.3)
            option_pool = min(option_pool, 0.2)  # ponytail: 钳到常规上限，超限场景属输入错误
        dilution = max(0.0, min(dilution, 1.0))
        option_pool = max(0.0, min(option_pool, 1.0))
        
        # 计算后股权结构
        post_money_structure = []
        
        # 创始人（稀释后）
        for sh in shareholders:
            post_money_structure.append({
                'name': sh.get('name', ''),
                'type': 'founder',
                'ratio': sh.get('ratio', 0) * (1 - dilution - option_pool),
                'holding_method': '通过持股平台间接持股'
            })
        
        # 投资人
        post_money_structure.append({
            'name': financing.get('investor', '投资方'),
            'type': 'investor',
            'ratio': dilution,
            'holding_method': '直接持股'
        })
        
        # 期权池
        post_money_structure.append({
            'name': '员工持股平台（期权池）',
            'type': 'option_pool',
            'ratio': option_pool,
            'holding_method': '通过持股平台代持'
        })
        
        return {
            'pre_money': shareholders,
            'post_money': post_money_structure,
            'dilution': dilution,
            'option_pool': option_pool
        }
    
    def _design_control(self, equity_structure, requirements):
        """设计控制权方案"""
        post_money = equity_structure.get('post_money', [])
        
        # 计算创始人总持股
        founder_ratio = sum([s['ratio'] for s in post_money if s['type'] == 'founder'])
        
        control_methods = []
        
        # 67%绝对控制线
        if founder_ratio >= 0.67:
            control_methods.append({
                'method': '股权控制',
                'description': f'创始人合计持股{founder_ratio*100:.1f}%，达到67%绝对控制线',
                'strength': 'strong'
            })
        # 51%相对控制线
        elif founder_ratio >= 0.51:
            control_methods.append({
                'method': '股权控制',
                'description': f'创始人合计持股{founder_ratio*100:.1f}%，达到51%相对控制线',
                'strength': 'medium'
            })
        # 34%以下需要加固
        else:
            control_methods.extend([
                {
                    'method': '一致行动人协议',
                    'description': '所有创始人签署一致行动人协议，共同行使表决权',
                    'strength': 'medium'
                },
                {
                    'method': '章程特别条款',
                    'description': '章程约定重大事项需创始人67%以上同意',
                    'strength': 'medium'
                },
                {
                    'method': '委托投票权',
                    'description': '投资人将部分表决权委托给创始人',
                    'strength': 'weak'
                }
            ])
        
        # 持股平台GP控制
        control_methods.append({
            'method': '持股平台GP',
            'description': '创始人担任持股平台普通合伙人（GP），享有100%表决权',
            'strength': 'strong'
        })
        
        return {
            'founder_ratio': founder_ratio,
            'control_level': 'strong' if founder_ratio >= 0.67 else 'medium' if founder_ratio >= 0.51 else 'weak',
            'methods': control_methods
        }
    
    def _tax_optimization(self, equity_structure):
        """税务筹划建议"""
        return {
            '持股平台注册地': {
                'recommendation': '以业务与政策稳定性选址，不依赖核定征收型税收洼地',
                'benefit': '权益性投资的合伙企业一律查账征收（税务总局公告2021年第41号），财政返还不可持续且有追溯风险',
                'estimated_saving': '洼地套利不再计入筹划收益'
            },
            '递延纳税备案': {
                'recommendation': '按财税101号文办理递延纳税备案',
                'benefit': '员工行权时递延纳税至转让股权时',
                'tax_rate': '20%（财产转让所得）vs 45%（工资薪金所得）'
            },
            '分红路径': {
                'recommendation': '公司→合伙平台→自然人LP：穿透后股息红利仍按20%个税（国税函〔2001〕84号），平台不降低分红税负',
                'benefit': '合伙层的作用是控制权集中与风险隔离，不是分红省税；激励个税递延按财税101号文办理'
            }
        }
    
    def _valuation_adjustment_terms(self, financing):
        """对赌条款建议"""
        return {
            '对赌主体': {
                'recommendation': '创始人（非目标公司）',
                'reason': '根据《九民纪要》，与目标公司对赌需履行减资程序',
                'risk_level': 'low'
            },
            '业绩承诺': {
                'recommendation': '未来3年累计净利润不低于X万元',
                'calculation': '估值依据的3倍PE对应的净利润',
                'adjustment': '允许±10%的波动范围'
            },
            '回购条款': {
                'trigger': ['IPO失败', '业绩不达标', '重大违约'],
                'price': '投资款 + 年化8-12%收益',
                'recommendation': '避免固定收益条款（违反九民纪要）'
            },
            '反稀释': {
                'method': '加权平均法',
                'reason': '相比完全棘轮，对创始人更友好'
            }
        }
    
    def _implementation_steps(self, template, equity_structure):
        """实施步骤"""
        steps = []
        
        # 第1步：设立持股平台
        steps.append({
            'step': 1,
            'action': '设立有限合伙持股平台',
            'details': [
                '设立创始人持股平台（有限合伙企业）',
                '设立员工持股平台（有限合伙企业）',
                '创始人担任GP，享有管理权和表决权'
            ],
            'timeline': '2周',
            'cost': '工商注册费用约5000元'
        })
        
        # 第2步：股权转入平台
        steps.append({
            'step': 2,
            'action': '创始人股权转入持股平台',
            'details': [
                '创始人将目标公司股权平价转让给持股平台',
                '办理工商变更登记',
                '无税务负担（平价转让）'
            ],
            'timeline': '3周',
            'cost': '工商变更费用约2000元'
        })
        
        # 第3步：期权池代持
        steps.append({
            'step': 3,
            'action': '期权池预留（代持）',
            'details': [
                '员工持股平台预留15%期权池',
                '由GP代持，待授予时转让',
                '签署代持协议'
            ],
            'timeline': '1周',
            'cost': '无'
        })
        
        # 第4步：投资人进入
        steps.append({
            'step': 4,
            'action': '投资人增资入股',
            'details': [
                '投资人与创始人签署对赌协议',
                '投资人向目标公司增资',
                '办理工商变更'
            ],
            'timeline': '4周',
            'cost': '律师费约5-10万元'
        })
        
        # 第5步：章程修改
        steps.append({
            'step': 5,
            'action': '修改公司章程',
            'details': [
                '加入控制权保护条款',
                '约定重大事项特别表决比例',
                '明确股东权利义务'
            ],
            'timeline': '1周',
            'cost': '律师费约2万元'
        })
        
        # 第6步：税务备案
        steps.append({
            'step': 6,
            'action': '办理税务备案',
            'details': [
                '持股平台办理税务登记',
                '员工激励办理递延纳税备案（101号文）',
                '确认税收优惠政策适用'
            ],
            'timeline': '2周',
            'cost': '无'
        })
        
        return steps
    
    def _generate_recommendations(self, equity_structure, ipo_plan):
        """生成综合建议"""
        recommendations = []
        
        # 控制权建议
        founder_ratio = sum([s['ratio'] for s in equity_structure.get('post_money', []) 
                            if s['type'] == 'founder'])
        if founder_ratio < 0.34:
            recommendations.append({
                'category': '控制权',
                'priority': 'P0',
                'issue': '创始人持股低于34%一票否决线',
                'recommendation': '建议：签署一致行动人协议 + 章程特别条款 + 委托投票权',
                'impact': '避免失去控制权'
            })
        
        # 期权池建议
        option_pool = equity_structure.get('option_pool', 0)
        if option_pool < 0.10:
            recommendations.append({
                'category': '员工激励',
                'priority': 'P1',
                'issue': '期权池预留不足10%',
                'recommendation': '建议预留15-20%期权池，分3-4年授予',
                'impact': '确保长期激励空间'
            })
        
        # 上市合规建议
        if ipo_plan.get('target') in ['科创板', '创业板']:
            recommendations.append({
                'category': '上市合规',
                'priority': 'P1',
                'issue': '境内上市需满足实际控制人2年不变更',
                'recommendation': '架构搭建后2年内不应发生控制权变更',
                'impact': '影响上市进度'
            })
        
        return recommendations
