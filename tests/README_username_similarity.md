# 用户名相似性测试 - 说明文档

## 概述

`test_username_similarity.py` 是一个标准的 unittest 测试套件，用于测试 ZxcvbnInstance 的 `set_passwd_and_input()` 方法在检测密码中包含用户名方面的能力。

## 功能说明

此测试套件验证了临时用户输入功能能够：
- 检测密码中包含的用户名
- 正确降低包含用户名的密码强度评分
- 确保临时用户输入不会污染实例缓存
- 支持中英文环境
- 处理各种边界情况

## 测试用例

### 1. 密码包含用户名测试（5个测试）
- `test_password_contains_full_username_capitalized` - 大写开头的完整用户名
- `test_password_contains_full_username_zhangsan` - 测试 zhangsan 用户
- `test_password_contains_full_username_lisi` - 测试 lisi 用户
- `test_password_contains_full_username_wangwu` - 测试 wangwu 用户
- `test_password_contains_partial_username` - 部分用户名

### 2. 密码不含用户名测试（2个测试）
- `test_password_without_username_strong` - 较强密码但不含用户名
- `test_password_without_username_weak_numbers` - 弱密码（纯数字）

### 3. 特殊场景测试（4个测试）
- `test_password_without_username_provided` - 未提供用户名
- `test_temp_user_inputs_isolation` - 临时输入隔离性验证
- `test_username_detection_english` - 英文环境测试
- `test_username_detection_chinese` - 中文环境测试

### 4. 边界情况测试（3个测试）
- `test_empty_username` - 空用户名处理
- `test_username_same_as_password` - 用户名与密码相同
- `test_username_with_special_characters` - 特殊字符用户名

## 运行方式

### 方式1：独立运行
```bash
cd /Users/liuk/src/zxcvbn-python
python3 tests/test_username_similarity.py
```

输出示例：
```
================================================================================
ZxcvbnInstance 用户名检测测试套件
测试 set_passwd_and_input() 方法的临时用户输入功能
================================================================================

test_empty_username ... ok
test_password_contains_full_username_capitalized ... ok
...

----------------------------------------------------------------------
Ran 14 tests in 0.031s

OK
```

### 方式2：使用 unittest 模块运行
```bash
cd /Users/liuk/src/zxcvbn-python
python3 -m unittest tests.test_username_similarity -v
```

### 方式3：运行所有测试
```bash
cd /Users/liuk/src/zxcvbn-python
python3 -m unittest discover -s tests -p "test_*.py"
```

## 测试架构

### 核心类
- `TestUsernameInPassword(unittest.TestCase)` - 主测试类

### 辅助方法
- `_analyze_password()` - 分析密码强度（封装 set_passwd_and_input 调用）
- `_check_contains_username_warning()` - 检查是否有用户名相关警告
- `_check_username_in_matches()` - 检查匹配序列中是否包含用户名

### 测试设置
- `setUpClass()` - 创建共享的 ZxcvbnInstance 实例（英文和中文）

## 关键验证点

### 1. 临时用户输入功能
```python
result = zx.set_passwd_and_input(
    password='Alice123',
    temp_user_inputs=['alice', 'alice@example.com']
)
```

### 2. 用户名检测
验证 `sequence` 中包含 `dictionary_name='user_inputs'` 的匹配项

### 3. 分数验证
- 包含用户名：分数 ≤ 2
- 不含用户名且较强：分数 ≥ 1
- 用户名与密码相同：分数 = 0

### 4. 隔离性验证
确保不同评估之间的临时用户输入不会相互影响

## 与原测试脚本的对比

### 原测试脚本特点
- 使用 Django 框架
- 依赖 `shared_resources.password_checker.analyze_password`
- 脚本式输出，适合手动查看

### 新测试套件特点
- 标准 unittest.TestCase
- 直接使用 ZxcvbnInstance
- 自动化断言，适合 CI/CD
- 支持独立运行和集成运行

## 测试覆盖

| 功能 | 覆盖情况 |
|------|---------|
| 用户名检测 | ✅ 完整覆盖 |
| 临时输入隔离 | ✅ 完整覆盖 |
| 多语言支持 | ✅ 中英文 |
| 边界情况 | ✅ 完整覆盖 |
| 性能验证 | ⚠️ 未包含（可扩展）|

## 扩展建议

如需扩展测试，可以添加：
1. 性能测试（大量用户名场景）
2. 更多语言环境测试
3. 线程安全性测试（多线程并发）
4. 更复杂的用户名模式（email、中文名等）

## 依赖

- Python 3.8+
- zxcvbn-python 库
- unittest（Python 标准库）

## 相关文件

- `/Users/liuk/src/zxcvbn-python/zxcvbn/zxcvbn_class.py` - ZxcvbnInstance 实现
- `/Users/liuk/src/zxcvbn-python/tests/test_zxcvbn_instance.py` - 其他 ZxcvbnInstance 测试
- `/Users/liuk/src/zxcvbn-python/TEMP_USER_INPUTS_GUIDE.md` - 临时用户输入功能指南

## 维护说明

- 测试用例基于实际使用场景设计
- 如果 ZxcvbnInstance API 变更，需相应更新测试
- 定期运行测试以确保功能稳定性
