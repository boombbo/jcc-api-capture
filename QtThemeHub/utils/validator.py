"""
主题验证器模块

提供主题验证功能，确保主题文件的有效性
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from ..core.loader import ThemeMeta


def validate_theme(theme: Union[str, Path, ThemeMeta]) -> Tuple[bool, List[str]]:
    """验证主题的有效性
    
    Args:
        theme: 主题路径、内容或元数据
        
    Returns:
        验证结果和错误信息列表
    """
    errors = []
    
    # 获取主题内容
    if isinstance(theme, ThemeMeta):
        if theme.path:
            try:
                content = theme.path.read_text(encoding='utf-8')
            except Exception as e:
                errors.append(f"无法读取主题文件: {e}")
                return False, errors
        elif theme.loader:
            try:
                content = theme.loader()
            except Exception as e:
                errors.append(f"无法加载主题: {e}")
                return False, errors
        else:
            errors.append("主题元数据缺少路径或加载器")
            return False, errors
    elif isinstance(theme, (str, Path)):
        if isinstance(theme, str) and not Path(theme).exists():
            # 假设是主题内容
            content = theme
        else:
            # 假设是文件路径
            try:
                path = Path(theme)
                content = path.read_text(encoding='utf-8')
            except Exception as e:
                errors.append(f"无法读取主题文件: {e}")
                return False, errors
    else:
        errors.append(f"不支持的主题类型: {type(theme)}")
        return False, errors
    
    # 验证主题内容
    if not content.strip():
        errors.append("主题内容为空")
        return False, errors
    
    # 验证CSS语法
    syntax_errors = validate_css_syntax(content)
    if syntax_errors:
        errors.extend(syntax_errors)
        return False, errors
    
    # 验证选择器
    selector_errors = validate_selectors(content)
    if selector_errors:
        errors.extend(selector_errors)
    
    # 验证属性
    property_errors = validate_properties(content)
    if property_errors:
        errors.extend(property_errors)
    
    return len(errors) == 0, errors


def validate_css_syntax(content: str) -> List[str]:
    """验证CSS语法
    
    Args:
        content: CSS内容
        
    Returns:
        错误信息列表
    """
    errors = []
    
    # 检查括号是否匹配
    if content.count('{') != content.count('}'):
        errors.append("CSS括号不匹配")
    
    # 检查是否有未闭合的注释
    if '/*' in content and '*/' not in content:
        errors.append("CSS注释未闭合")
    
    # 检查是否有语法错误的选择器
    lines = content.split('\n')
    for i, line in enumerate(lines):
        line = line.strip()
        if '{' in line and '}' in line and line.index('{') > line.index('}'):
            errors.append(f"第{i+1}行: 括号顺序错误")
        
        if line.endswith('{') and i+1 < len(lines) and '}' in lines[i+1].strip() and not lines[i+1].strip().startswith('}'):
            errors.append(f"第{i+2}行: 可能缺少属性")
    
    return errors


def validate_selectors(content: str) -> List[str]:
    """验证选择器
    
    Args:
        content: CSS内容
        
    Returns:
        错误信息列表
    """
    errors = []
    
    # 提取所有选择器
    selectors = re.findall(r'([^{]+){', content)
    
    for selector in selectors:
        selector = selector.strip()
        
        # 检查选择器是否为空
        if not selector:
            errors.append(f"发现空选择器")
            continue
        
        # 检查选择器是否有语法错误
        if selector.count('(') != selector.count(')'):
            errors.append(f"选择器括号不匹配: {selector}")
        
        # 检查选择器是否有无效字符
        invalid_chars = re.findall(r'[^\w\s\-_\.#:,>\+\~\[\]\(\)=\*\^$|"]', selector)
        if invalid_chars:
            errors.append(f"选择器包含无效字符 {', '.join(set(invalid_chars))}: {selector}")
    
    return errors


def validate_properties(content: str) -> List[str]:
    """验证属性
    
    Args:
        content: CSS内容
        
    Returns:
        错误信息列表
    """
    errors = []
    
    # 提取所有属性块
    blocks = re.findall(r'{([^}]*)}', content)
    
    for block in blocks:
        # 分割属性
        properties = [p.strip() for p in block.split(';') if p.strip()]
        
        for prop in properties:
            # 检查属性格式
            if ':' not in prop:
                errors.append(f"属性格式错误 (缺少冒号): {prop}")
                continue
            
            # 分割属性名和值
            parts = prop.split(':', 1)
            name = parts[0].strip()
            value = parts[1].strip()
            
            # 检查属性名是否为空
            if not name:
                errors.append(f"属性名为空: {prop}")
            
            # 检查属性值是否为空
            if not value:
                errors.append(f"属性值为空: {prop}")
    
    return errors 
