"""
样式优化器模块

提供样式表优化和处理功能
"""

import re
from typing import Dict, List, Optional


def optimize_stylesheet(stylesheet: str) -> str:
    """优化样式表
    
    Args:
        stylesheet: 原始样式表
        
    Returns:
        优化后的样式表
    """
    # 移除注释
    stylesheet = remove_comments(stylesheet)
    
    # 压缩空白字符
    stylesheet = compress_whitespace(stylesheet)
    
    # 修复Qt绑定差异
    stylesheet = fix_binding_differences(stylesheet)
    
    return stylesheet


def remove_comments(stylesheet: str) -> str:
    """移除CSS注释
    
    Args:
        stylesheet: 原始样式表
        
    Returns:
        移除注释后的样式表
    """
    # 移除/* */注释
    stylesheet = re.sub(r'/\*.*?\*/', '', stylesheet, flags=re.DOTALL)
    
    # 移除//注释
    stylesheet = re.sub(r'//.*?$', '', stylesheet, flags=re.MULTILINE)
    
    return stylesheet


def compress_whitespace(stylesheet: str) -> str:
    """压缩空白字符
    
    Args:
        stylesheet: 原始样式表
        
    Returns:
        压缩空白字符后的样式表
    """
    # 将多个空白字符替换为单个空格
    stylesheet = re.sub(r'\s+', ' ', stylesheet)
    
    # 移除选择器后的空格
    stylesheet = re.sub(r'([,{;]) ', r'\1', stylesheet)
    
    # 移除属性前的空格
    stylesheet = re.sub(r' ([}])', r'\1', stylesheet)
    
    # 保留换行符以提高可读性
    stylesheet = re.sub(r'([;}]) ', r'\1\n', stylesheet)
    
    return stylesheet


def fix_binding_differences(stylesheet: str) -> str:
    """修复不同Qt绑定之间的差异
    
    Args:
        stylesheet: 原始样式表
        
    Returns:
        修复后的样式表
    """
    # 修复Qt5和Qt6之间的类名差异
    replacements = {
        # Qt5 -> Qt6
        'QAction': 'QAction, QtGui.QAction',
        'QCheckBox': 'QCheckBox, QtWidgets.QCheckBox',
        'QComboBox': 'QComboBox, QtWidgets.QComboBox',
        'QDialog': 'QDialog, QtWidgets.QDialog',
        'QFrame': 'QFrame, QtWidgets.QFrame',
        'QGroupBox': 'QGroupBox, QtWidgets.QGroupBox',
        'QLabel': 'QLabel, QtWidgets.QLabel',
        'QLineEdit': 'QLineEdit, QtWidgets.QLineEdit',
        'QListView': 'QListView, QtWidgets.QListView',
        'QMainWindow': 'QMainWindow, QtWidgets.QMainWindow',
        'QMenu': 'QMenu, QtWidgets.QMenu',
        'QMenuBar': 'QMenuBar, QtWidgets.QMenuBar',
        'QPushButton': 'QPushButton, QtWidgets.QPushButton',
        'QRadioButton': 'QRadioButton, QtWidgets.QRadioButton',
        'QScrollBar': 'QScrollBar, QtWidgets.QScrollBar',
        'QSlider': 'QSlider, QtWidgets.QSlider',
        'QSpinBox': 'QSpinBox, QtWidgets.QSpinBox',
        'QStatusBar': 'QStatusBar, QtWidgets.QStatusBar',
        'QTabBar': 'QTabBar, QtWidgets.QTabBar',
        'QTabWidget': 'QTabWidget, QtWidgets.QTabWidget',
        'QToolBar': 'QToolBar, QtWidgets.QToolBar',
        'QToolButton': 'QToolButton, QtWidgets.QToolButton',
        'QTreeView': 'QTreeView, QtWidgets.QTreeView',
        'QWidget': 'QWidget, QtWidgets.QWidget'
    }
    
    # 只替换选择器部分，不替换属性值中的类名
    lines = stylesheet.split('\n')
    result = []
    
    in_selector = True
    for line in lines:
        if '{' in line:
            selector_part = line.split('{')[0]
            rest_part = '{'.join(line.split('{')[1:])
            
            # 替换选择器中的类名
            for old, new in replacements.items():
                # 确保只替换完整的类名，而不是部分匹配
                selector_part = re.sub(r'(^|\s|,)' + old + r'($|\s|[,\.:#])', r'\1' + new + r'\2', selector_part)
            
            result.append(selector_part + '{' + rest_part)
            in_selector = False
        elif '}' in line:
            result.append(line)
            in_selector = True
        else:
            result.append(line)
    
    return '\n'.join(result) 
