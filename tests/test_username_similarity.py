#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户名相似性测试 - 基于 unittest.TestCase
测试 ZxcvbnInstance 的 set_passwd_and_input 方法检测密码中的用户名

此测试套件验证临时用户输入功能能否正确识别密码中包含的用户名，
确保密码策略能够防止用户使用包含用户名的弱密码。
"""

import unittest
import sys
import os

# 确保可以导入 zxcvbn 模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from zxcvbn import ZxcvbnInstance


class TestUsernameInPassword(unittest.TestCase):
    """
    测试密码中的用户名检测功能。
    
    使用 ZxcvbnInstance 的 set_passwd_and_input() 方法，将用户名作为
    临时用户输入传递，验证系统能够正确识别和警告包含用户名的密码。
    """
    
    @classmethod
    def setUpClass(cls):
        """设置测试类 - 创建共享的 ZxcvbnInstance 实例"""
        cls.zx_en = ZxcvbnInstance(lang='en', thread_safe=False)
        cls.zx_zh = ZxcvbnInstance(lang='zh_Hans', thread_safe=False)
    
    def _analyze_password(self, password, username=None, lang='en'):
        """
        分析密码强度，可选传入用户名。
        
        Args:
            password (str): 待分析的密码
            username (str, optional): 用户名，将作为临时用户输入
            lang (str): 语言，'en' 或 'zh'
            
        Returns:
            dict: 包含分析结果的字典
        """
        # 选择对应语言的实例
        zx = self.zx_zh if lang == 'zh' else self.zx_en
        
        # 构建临时用户输入列表
        temp_user_inputs = None
        if username:
            # 包含原始用户名和小写版本
            temp_user_inputs = [username, username.lower()]
        
        # 使用 set_passwd_and_input 进行分析
        result = zx.set_passwd_and_input(password, temp_user_inputs=temp_user_inputs)
        
        return result
    
    def _check_contains_username_warning(self, result):
        """
        检查结果中是否包含用户名相关的警告。
        
        Args:
            result (dict): zxcvbn 分析结果
            
        Returns:
            bool: 是否包含用户名警告
        """
        feedback = result.get('feedback', {})
        warning = feedback.get('warning', '')
        
        if not warning:
            return False
        
        warning_lower = warning.lower()
        # 检查常见的用户名相关警告关键词（英文和中文）
        keywords = ['name', 'user', '用户名', 'personal', 'common', 'surname', '姓名']
        return any(keyword in warning_lower for keyword in keywords)
    
    def _check_username_in_matches(self, result, username):
        """
        检查匹配序列中是否包含用户名匹配。
        
        Args:
            result (dict): zxcvbn 分析结果
            username (str): 用户名
            
        Returns:
            bool: 是否在匹配中发现用户名
        """
        sequence = result.get('sequence', [])
        username_lower = username.lower() if username else ''
        
        for match in sequence:
            if match.get('dictionary_name') == 'user_inputs':
                matched_word = match.get('matched_word', '').lower()
                if matched_word == username_lower or username_lower in matched_word:
                    return True
        return False
    
    # ========== 测试用例：密码包含完整用户名 ==========
    
    def test_password_contains_full_username_capitalized(self):
        """测试：密码包含完整用户名（大写开头）- liruping/Liruping123"""
        username = 'liruping'
        password = 'Liruping123'
        
        result = self._analyze_password(password, username, lang='zh')
        
        # 验证分数应该较低（因为包含用户名）
        self.assertLessEqual(result['score'], 2, 
            f"密码 '{password}' 包含用户名 '{username}'，分数应该较低")
        
        # 验证匹配中包含用户名
        has_username_match = self._check_username_in_matches(result, username)
        self.assertTrue(has_username_match,
            f"密码 '{password}' 应该在匹配中检测到用户名 '{username}'")
    
    def test_password_contains_full_username_zhangsan(self):
        """测试：密码包含完整用户名 - zhangsan/Zhangsan123"""
        username = 'zhangsan'
        password = 'Zhangsan123'
        
        result = self._analyze_password(password, username, lang='zh')
        
        self.assertLessEqual(result['score'], 2,
            f"密码 '{password}' 包含用户名 '{username}'，分数应该较低")
        
        has_username_match = self._check_username_in_matches(result, username)
        self.assertTrue(has_username_match,
            f"密码 '{password}' 应该在匹配中检测到用户名 '{username}'")
    
    def test_password_contains_full_username_lisi(self):
        """测试：密码包含完整用户名 - lisi/Lisi@2024"""
        username = 'lisi'
        password = 'Lisi@2024'
        
        result = self._analyze_password(password, username, lang='zh')
        
        self.assertLessEqual(result['score'], 2,
            f"密码 '{password}' 包含用户名 '{username}'，分数应该较低")
        
        has_username_match = self._check_username_in_matches(result, username)
        self.assertTrue(has_username_match,
            f"密码 '{password}' 应该在匹配中检测到用户名 '{username}'")
    
    def test_password_contains_full_username_wangwu(self):
        """测试：密码包含完整用户名 - wangwu/Wangwu999!"""
        username = 'wangwu'
        password = 'Wangwu999!'
        
        result = self._analyze_password(password, username, lang='zh')
        
        self.assertLessEqual(result['score'], 2,
            f"密码 '{password}' 包含用户名 '{username}'，分数应该较低")
        
        has_username_match = self._check_username_in_matches(result, username)
        self.assertTrue(has_username_match,
            f"密码 '{password}' 应该在匹配中检测到用户名 '{username}'")
    
    # ========== 测试用例：密码包含部分用户名 ==========
    
    def test_password_contains_partial_username(self):
        """测试：密码包含部分用户名 - liruping/Liruping!"""
        username = 'liruping'
        password = 'Liruping!'
        
        result = self._analyze_password(password, username, lang='zh')
        
        # 验证分数应该较低
        self.assertLessEqual(result['score'], 2,
            f"密码 '{password}' 包含用户名 '{username}'，分数应该较低")
        
        # 验证匹配中包含用户名
        has_username_match = self._check_username_in_matches(result, username)
        self.assertTrue(has_username_match,
            f"密码 '{password}' 应该在匹配中检测到用户名 '{username}'")
    
    # ========== 测试用例：密码不含用户名（强密码）==========
    
    def test_password_without_username_strong(self):
        """测试：密码不含用户名（较强密码）- liruping/Abcd1234!"""
        username = 'liruping'
        password = 'Abcd1234!'
        
        result = self._analyze_password(password, username, lang='zh')
        
        # 验证分数应该不低（不包含用户名）
        # 注意：Abcd1234 是常见模式，可能得分不高，但至少应该比纯数字高
        self.assertGreaterEqual(result['score'], 1,
            f"密码 '{password}' 不包含用户名，分数应该不为 0")
        
        # 验证匹配中不应包含用户名
        has_username_match = self._check_username_in_matches(result, username)
        self.assertFalse(has_username_match,
            f"密码 '{password}' 不应该在匹配中检测到用户名 '{username}'")
    
    # ========== 测试用例：密码不含用户名（弱密码）==========
    
    def test_password_without_username_weak_numbers(self):
        """测试：密码不含用户名（弱密码-纯数字）- liruping/12345678"""
        username = 'liruping'
        password = '12345678'
        
        result = self._analyze_password(password, username, lang='zh')
        
        # 验证分数应该很低（虽然不含用户名，但复杂度太低）
        self.assertLessEqual(result['score'], 1,
            f"密码 '{password}' 虽不含用户名但复杂度太低，分数应该很低")
        
        # 验证匹配中不应包含用户名
        has_username_match = self._check_username_in_matches(result, username)
        self.assertFalse(has_username_match,
            f"密码 '{password}' 不应该在匹配中检测到用户名 '{username}'")
    
    # ========== 测试用例：无用户名传递 ==========
    
    def test_password_without_username_provided(self):
        """测试：无用户名传递时的行为 - None/Liruping123"""
        password = 'Liruping123'
        
        # 不传递用户名
        result = self._analyze_password(password, username=None, lang='zh')
        
        # 验证结果有效
        self.assertIn('score', result)
        self.assertGreaterEqual(result['score'], 0)
        self.assertLessEqual(result['score'], 4)
        
        # 不应有用户名匹配（因为没有提供用户名）
        sequence = result.get('sequence', [])
        user_input_matches = [m for m in sequence if m.get('dictionary_name') == 'user_inputs']
        self.assertEqual(len(user_input_matches), 0,
            "未提供用户名时，不应有 user_inputs 字典匹配")
    
    # ========== 测试用例：验证临时输入不污染实例 ==========
    
    def test_temp_user_inputs_isolation(self):
        """测试：临时用户输入不会污染实例缓存"""
        username1 = 'alice'
        password1 = 'alice123'
        
        username2 = 'bob'
        password2 = 'alice123'  # 相同密码，不同用户名
        
        # 第一次评估：使用 alice 作为用户名
        result1 = self._analyze_password(password1, username1, lang='en')
        has_alice_match = self._check_username_in_matches(result1, username1)
        self.assertTrue(has_alice_match, "第一次评估应该检测到 alice")
        
        # 第二次评估：使用 bob 作为用户名，评估相同密码
        result2 = self._analyze_password(password2, username2, lang='en')
        has_bob_match = self._check_username_in_matches(result2, username2)
        has_alice_match_2 = self._check_username_in_matches(result2, username1)
        
        # bob 不应该被检测到（因为密码中没有 bob）
        self.assertFalse(has_bob_match, "第二次评估不应该检测到 bob")
        
        # alice 也不应该被检测到（因为临时输入应该是独立的）
        self.assertFalse(has_alice_match_2, 
            "第二次评估不应该检测到 alice（临时输入应该隔离）")
    
    # ========== 测试用例：验证不同语言 ==========
    
    def test_username_detection_english(self):
        """测试：英文环境下的用户名检测"""
        username = 'myuser'
        password = 'Myuser123!'
        
        result = self._analyze_password(password, username, lang='en')
        
        # 验证能检测到用户名
        has_username_match = self._check_username_in_matches(result, username)
        self.assertTrue(has_username_match,
            f"英文环境应该检测到密码中的用户名 '{username}'")
        
        # 验证分数受影响
        self.assertLessEqual(result['score'], 2,
            "包含用户名的密码分数应该较低")
    
    def test_username_detection_chinese(self):
        """测试：中文环境下的用户名检测"""
        username = 'zhang'
        password = 'Zhang123!'
        
        result = self._analyze_password(password, username, lang='zh')
        
        # 验证能检测到用户名
        has_username_match = self._check_username_in_matches(result, username)
        self.assertTrue(has_username_match,
            f"中文环境应该检测到密码中的用户名 '{username}'")
        
        # 验证分数受影响
        self.assertLessEqual(result['score'], 2,
            "包含用户名的密码分数应该较低")
    
    # ========== 测试用例：边界情况 ==========
    
    def test_empty_username(self):
        """测试：空用户名的处理"""
        password = 'Abcd1234!'
        
        result = self._analyze_password(password, username='', lang='en')
        
        # 验证结果有效
        self.assertIn('score', result)
        self.assertGreaterEqual(result['score'], 0)
    
    def test_username_same_as_password(self):
        """测试：用户名与密码完全相同"""
        username = 'test123'
        password = 'test123'
        
        result = self._analyze_password(password, username, lang='en')
        
        # 验证分数应该非常低
        self.assertEqual(result['score'], 0,
            "用户名与密码相同时，分数应该为 0")
        
        # 验证能检测到用户名
        has_username_match = self._check_username_in_matches(result, username)
        self.assertTrue(has_username_match,
            "应该检测到用户名与密码相同")
    
    def test_username_with_special_characters(self):
        """测试：包含特殊字符的用户名"""
        username = 'user.name'
        password = 'User.name123'
        
        result = self._analyze_password(password, username, lang='en')
        
        # 至少应该有结果
        self.assertIn('score', result)
        self.assertIsNotNone(result.get('feedback'))


def suite():
    """创建测试套件"""
    test_suite = unittest.TestSuite()
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestUsernameInPassword))
    return test_suite


if __name__ == '__main__':
    # 支持独立运行
    print("\n" + "=" * 80)
    print("ZxcvbnInstance 用户名检测测试套件")
    print("测试 set_passwd_and_input() 方法的临时用户输入功能")
    print("=" * 80 + "\n")
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite())
    
    # 输出汇总
    print("\n" + "=" * 80)
    print("测试汇总")
    print("=" * 80)
    print(f"运行测试: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print("=" * 80)
    
    # 返回适当的退出码
    sys.exit(0 if result.wasSuccessful() else 1)
