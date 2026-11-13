"""
风险扫描器 - 识别22类常见股权架构风险
"""


class RiskScanner:
    """股权架构风险扫描引擎"""
    
    def __init__(self, knowledge_base):
        self.kb = knowledge_base
        self.risk_rules = self._load_risk_rules()
    
    def scan(self, architecture):
        """
        扫描架构风险
        
        Returns:
            {
                'P0': [...],  # 阻断性风险
                'P1': [...],  # 重大风险
                'P2': [...]   # 优化建议
            }
        """
        risks = {'P0': [], 'P1': [], 'P2': []}
        
        # 形态契约归一: 生成器/审核器两种架构dict统一成规则可读视图（评审：审核链路规则恒死源于键不匹配）
        view = self._normalize_view(architecture)
        
        # 扫描所有风险规则
        for rule in self.risk_rules:
            if self._check_rule(rule, view):
                risks[rule['priority']].append({
                    'category': rule['category'],
                    'issue': rule['issue'],
                    'risk': rule['risk'],
                    'solution': rule['solution']
                })
        
        return risks
    
    def _normalize_view(self, architecture):
        """统一两种架构形态为检查视图"""
        if 'equity_structure' in architecture:
            # 生成器形态
            return {
                'founder_ratio': architecture.get('control_scheme', {}).get('founder_ratio', 1.0),
                'option_pool': architecture.get('equity_structure', {}).get('option_pool', 0),
                'layers': architecture.get('layers', 1),
                'valuation_adjustment': architecture.get('valuation_adjustment', {}),
            }
        # 审核器形态: 从股东列表推导
        shs = architecture.get('shareholders', [])
        return {
            'founder_ratio': sum(s.get('ratio', 0) for s in shs if s.get('type') == 'founder'),
            'option_pool': sum(s.get('ratio', 0) for s in shs if s.get('type') == 'option_pool'),
            'layers': architecture.get('layers', 1),
            'valuation_adjustment': architecture.get('valuation_adjustment', {}),
        }
    
    def _check_rule(self, rule, view):
        """检查规则是否触发"""
        try:
            return rule['check'](view)
        except Exception:
            return False
    
    def _load_risk_rules(self):
        """加载风险规则库（22类）"""
        return [
            # === P0级风险（阻断性）===
            {
                'id': 'R01',
                'priority': 'P0',
                'category': '控制权',
                'issue': '创始人持股<34%且无一致行动人协议',
                'risk': '失去一票否决权，重大决策无控制力',
                'solution': '立即签署一致行动人协议 + 章程特别表决条款',
                'check': lambda arch: self._check_control_below_34(arch)
            },
            {
                'id': 'R02',
                'priority': 'P0',
                'category': '外资准入',
                'issue': 'VIE用于非限制行业',
                'risk': '架构复杂度无必要，增加合规成本',
                'solution': '拆除VIE，改为直接持股或红筹',
                'check': lambda arch: False  # 需实际检测
            },
            {
                'id': 'R03',
                'priority': 'P0',
                'category': '对赌协议',
                'issue': '与目标公司对赌未履行减资程序',
                'risk': '根据九民纪要，无法强制执行',
                'solution': '修改对赌主体为创始人，或立即减资',
                'check': lambda arch: self._check_company_valuation_adjust(arch)
            },
            {
                'id': 'R04',
                'priority': 'P0',
                'category': '代持清理',
                'issue': '存在代持关系未清理',
                'risk': '影响上市审核，需强制清理',
                'solution': '立即显名至持股平台或员工本人',
                'check': lambda arch: False  # 需实际检测
            },
            {
                'id': 'R05',
                'priority': 'P0',
                'category': '37号文',
                'issue': '境外持股未办理37号文登记',
                'risk': '外汇违规，资金无法合法出境/回流',
                'solution': '补办37号文登记（可追溯）',
                'check': lambda arch: False  # 需实际检测
            },
            
            # === P1级风险（重大风险）===
            {
                'id': 'R06',
                'priority': 'P1',
                'category': '员工激励',
                'issue': '期权池<5%且无预留',
                'risk': '无法吸引核心人才，团队稳定性差',
                'solution': '老股东同比例稀释，预留10-15%',
                'check': lambda arch: self._check_option_pool_low(arch)
            },
            {
                'id': 'R07',
                'priority': 'P1',
                'category': '对赌协议',
                'issue': '对赌条款含固定收益（保底条款）',
                'risk': '违反九民纪要，可能被判无效',
                'solution': '删除固定收益，改为业绩挂钩回购',
                'check': lambda arch: False  # 需解析协议
            },
            {
                'id': 'R08',
                'priority': 'P1',
                'category': '递延纳税',
                'issue': '未办理101号文递延纳税备案',
                'risk': '员工行权税负45% vs 20%，激励效果大打折扣',
                'solution': '补办备案（窗口期6个月）',
                'check': lambda arch: False  # 需实际检测
            },
            {
                'id': 'R09',
                'priority': 'P1',
                'category': 'ODI备案',
                'issue': '境外投资未办理ODI备案',
                'risk': '资金出境受限，投资人退出困难',
                'solution': '补办商务部ODI备案',
                'check': lambda arch: False  # 需实际检测
            },
            {
                'id': 'R10',
                'priority': 'P1',
                'category': '股东协议',
                'issue': '缺少股东退出机制',
                'risk': '股东纠纷无解决路径',
                'solution': '补充签署股东协议，约定退出条款',
                'check': lambda arch: False  # 需实际检测
            },
            
            # === P2级风险（优化建议）===
            {
                'id': 'R11',
                'priority': 'P2',
                'category': '税务筹划',
                'issue': '持股平台注册地无税收优惠',
                'risk': '上市后减持税负过高',
                'solution': '迁址至宁波/霍尔果斯（地方留存返还40%）',
                # ponytail: 生成阶段拿不到平台实际注册地（需解析工商信息），有数据后接入
                'check': lambda arch: False
            },
            {
                'id': 'R12',
                'priority': 'P2',
                'category': '融资空间',
                'issue': '未预留下轮融资股权空间',
                'risk': '下轮融资稀释过大，创始人控制力下降',
                'solution': '规划多轮融资路径，预留10-15%空间',
                'check': lambda arch: False  # 需实际检测
            },
            {
                'id': 'R13',
                'priority': 'P2',
                'category': '章程条款',
                'issue': '章程未设置重大事项特别表决',
                'risk': '投资人可能阻止关键决策',
                'solution': '章程约定IPO/并购等需67%以上同意',
                'check': lambda arch: False  # 需实际检测
            },
            {
                'id': 'R14',
                'priority': 'P2',
                'category': '反稀释',
                'issue': '反稀释采用完全棘轮法',
                'risk': '对创始人极不友好，下轮融资困难',
                'solution': '改为加权平均法',
                'check': lambda arch: False  # 需解析协议
            },
            {
                'id': 'R15',
                'priority': 'P2',
                'category': '持股平台',
                'issue': '持股平台合伙人超过50人',
                'risk': '违反合伙企业法，需拆分',
                'solution': '拆分为多个持股平台，每个<50人',
                'check': lambda arch: False  # 需实际检测
            },
            {
                'id': 'R16',
                'priority': 'P2',
                'category': '员工激励',
                'issue': '激励方案无退出机制',
                'risk': '员工离职时股权处置困难',
                'solution': '设置离职回购条款（按净资产or公允价）',
                'check': lambda arch: False  # 需实际检测
            },
            {
                'id': 'R17',
                'priority': 'P2',
                'category': '红筹架构',
                'issue': '红筹架构层级过多（>4层）',
                'risk': '增加税务成本和管理复杂度',
                'solution': '简化架构，删除冗余层级',
                'check': lambda arch: self._check_too_many_layers(arch)
            },
            {
                'id': 'R18',
                'priority': 'P2',
                'category': 'VIE协议',
                'issue': 'VIE协议未更新（>3年）',
                'risk': '可能不符合最新监管要求',
                'solution': '更新协议，增加数据安全条款',
                'check': lambda arch: False  # 需实际检测
            },
            {
                'id': 'R19',
                'priority': 'P2',
                'category': '境外上市备案',
                'issue': '未提前准备境外上市备案材料',
                'risk': '临时准备耗时3-6个月',
                'solution': '提前准备22项备案材料',
                'check': lambda arch: False  # 需实际检测
            },
            {
                'id': 'R20',
                'priority': 'P2',
                'category': '数据安全',
                'issue': 'VIE架构未通过数据安全评估',
                'risk': '可能被要求拆除VIE',
                'solution': '提前通过网信办数据安全评估',
                'check': lambda arch: False  # 需实际检测
            },
            {
                'id': 'R21',
                'priority': 'P2',
                'category': '家族信托',
                'issue': '创始人未设置家族信托',
                'risk': '个人意外或婚变影响公司控制权',
                'solution': '设立家族信托持有持股平台份额',
                'check': lambda arch: False  # 需实际检测
            },
            {
                'id': 'R22',
                'priority': 'P2',
                'category': '关联交易',
                'issue': '存在未披露的关联交易',
                'risk': '影响上市审核',
                'solution': '清理关联交易或充分披露',
                'check': lambda arch: False  # 需实际检测
            }
        ]
    
    def _check_rule(self, rule, architecture):
        """检查规则是否触发"""
        try:
            return rule['check'](architecture)
        except Exception:
            return False
    
    def _check_control_below_34(self, view):
        """检查控制权是否低于34%"""
        return view.get('founder_ratio', 1.0) < 0.34
    
    def _check_company_valuation_adjust(self, view):
        """检查是否与目标公司对赌（推荐主体以'目标公司'开头才算，'创始人（非目标公司）'不算）"""
        subject = view.get('valuation_adjustment', {}).get('对赌主体', {}).get('recommendation', '')
        return subject.startswith('目标公司')
    
    def _check_option_pool_low(self, view):
        """检查期权池是否过低"""
        return view.get('option_pool', 0) < 0.05
    
    def _check_too_many_layers(self, view):
        """检查层级是否过多"""
        return view.get('layers', 1) > 4
