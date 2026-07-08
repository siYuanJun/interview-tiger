#!/usr/bin/env python3
"""
面试虎后端 API 解析脚本
支持三种模式：--scaffold（生成骨架）、--scan-only（盘点）、默认（验证）
"""

import os
import sys
import ast
import inspect
from pathlib import Path
from typing import List, Dict, Tuple

PROJECT_ROOT = "/Users/siyuan/Documents/www/ai-project/interview-tiger/backend"
ROUTE_PREFIX = "/api"
DOC_PATH = os.path.join(PROJECT_ROOT, "docs/接口全貌.md")

ROUTE_FILES = [
    "app/routes/health.py",
    "app/routes/config.py", 
    "app/routes/search.py",
    "app/routes/generate.py",
    "app/routes/question.py",
    "app/routes/asr.py",
    "app/routes/transcript.py",
]

MODULE_LABELS = {
    "health": "健康检查",
    "config": "配置管理",
    "search": "知识库检索",
    "generate": "大模型生成",
    "question": "问题处理",
    "asr": "语音识别",
    "transcript": "对话管理",
}


class RouteInfo:
    def __init__(self, method: str, path: str, func_name: str, 
                 params: List[Dict], return_type: str, docstring: str, module: str):
        self.method = method
        self.path = path
        self.func_name = func_name
        self.params = params
        self.return_type = return_type
        self.docstring = docstring
        self.module = module
    
    def to_dict(self):
        return {
            "method": self.method,
            "path": self.path,
            "func_name": self.func_name,
            "params": self.params,
            "return_type": self.return_type,
            "docstring": self.docstring,
            "module": self.module,
        }


def parse_pydantic_model(file_path: str, model_name: str) -> List[Dict]:
    """解析 Pydantic 模型字段"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    tree = ast.parse(content)
    fields = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == model_name:
            for item in node.body:
                if isinstance(item, ast.AnnAssign):
                    field_name = item.target.id
                    field_type = ast.dump(item.annotation) if item.annotation else "str"
                    description = ""
                    default_value = ""
                    
                    for sub in ast.walk(item):
                        if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name) and sub.func.id == "Field":
                            for kw in sub.keywords:
                                if kw.arg == "description":
                                    if isinstance(kw.value, ast.Constant):
                                        description = kw.value.value
                                elif kw.arg == "default":
                                    if isinstance(kw.value, ast.Constant):
                                        default_value = kw.value.value
                    
                    fields.append({
                        "name": field_name,
                        "type": field_type,
                        "source": "body",
                        "description": description,
                        "default": default_value
                    })
    return fields


def parse_route_file(file_path: str) -> List[RouteInfo]:
    """解析单个路由文件"""
    routes = []
    module_name = os.path.basename(file_path).replace(".py", "")
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    tree = ast.parse(content)
    function_defs = {}
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
            func_name = node.name
            docstring = ast.get_docstring(node) or ""
            
            params = []
            for arg in node.args.args:
                if arg.arg == "self":
                    continue
                
                arg_type = ""
                if arg.annotation:
                    arg_type = ast.dump(arg.annotation)
                    if "BaseModel" in arg_type or "Request" in arg_type:
                        model_name = arg.annotation.id
                        model_fields = parse_pydantic_model(file_path, model_name)
                        params.extend(model_fields)
                        continue
                
                params.append({
                    "name": arg.arg,
                    "type": arg_type,
                    "source": "query",
                    "description": "",
                    "default": ""
                })
            
            function_defs[func_name] = {
                "docstring": docstring,
                "params": params,
                "return_type": ""
            }
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
            func_name = node.name
            if func_name not in function_defs:
                continue
            
            func_info = function_defs[func_name]
            
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Call):
                    if isinstance(decorator.func, ast.Attribute) and isinstance(decorator.func.value, ast.Name):
                        if decorator.func.value.id == "router":
                            method = decorator.func.attr
                            if method in ["get", "post", "put", "delete", "websocket"]:
                                if decorator.args:
                                    path = decorator.args[0].s if isinstance(decorator.args[0], ast.Constant) else ""
                                    full_path = ROUTE_PREFIX + path
                                    routes.append(RouteInfo(
                                        method=method.upper(),
                                        path=full_path,
                                        func_name=func_name,
                                        params=func_info["params"],
                                        return_type=func_info["return_type"],
                                        docstring=func_info["docstring"],
                                        module=module_name
                                    ))
    
    return routes


def scan_all_routes() -> Dict[str, List[RouteInfo]]:
    """扫描所有路由文件"""
    result = {}
    for route_file in ROUTE_FILES:
        file_path = os.path.join(PROJECT_ROOT, route_file)
        if os.path.exists(file_path):
            routes = parse_route_file(file_path)
            module_name = os.path.basename(route_file).replace(".py", "")
            result[module_name] = routes
    return result


def generate_scaffold(routes_by_module: Dict[str, List[RouteInfo]]) -> str:
    """生成 Markdown 骨架"""
    lines = []
    lines.append("# 面试虎 - 后端接口全貌")
    lines.append("")
    lines.append("## 1. HTTP 接口总览")
    lines.append("")
    
    total_endpoints = 0
    
    for module_name, routes in routes_by_module.items():
        label = MODULE_LABELS.get(module_name, module_name)
        lines.append(f"### {label}")
        lines.append(f"")
        lines.append(f"端点数量: {len(routes)}")
        lines.append(f"")
        lines.append("| 请求方法 | 完整路径 | 参数 | 返回值类型 | 接口说明 |")
        lines.append("|----------|----------|------|------------|----------|")
        
        for route in routes:
            method = route.method
            path = route.path
            params_str = ", ".join([f"{p['name']}({p['type']})" for p in route.params]) if route.params else "-"
            return_type = route.return_type or "JSON"
            doc_summary = route.docstring.split("\n")[0].strip() if route.docstring else ""
            
            lines.append(f"| {method} | {path} | {params_str} | {return_type} | {doc_summary} |")
        
        lines.append("")
        total_endpoints += len(routes)
    
    lines.append(f"**接口总数**: {total_endpoints}")
    lines.append("")
    
    lines.append("## 2. 服务间调用")
    lines.append("")
    lines.append("| 调用方 | 被调用方 | 方法/路径 | 用途 |")
    lines.append("|--------|----------|-----------|------|")
    lines.append("| backend | 火山引擎方舟 | POST /api/v3/chat/completions | 大模型调用 |")
    lines.append("| backend | 火山引擎知识库 | POST /api/v1/rag/retrieve | 知识库检索 |")
    lines.append("| backend | 火山引擎ASR | WebSocket | 语音识别 |")
    lines.append("")
    
    lines.append("## 3. 消息队列通信")
    lines.append("")
    lines.append("本项目暂未使用消息队列。")
    lines.append("")
    
    return "\n".join(lines)


def scan_only(routes_by_module: Dict[str, List[RouteInfo]]):
    """盘点模式"""
    print("=== 接口盘点 ===")
    total = 0
    for module_name, routes in routes_by_module.items():
        label = MODULE_LABELS.get(module_name, module_name)
        print(f"\n{label}: {len(routes)} 个端点")
        for route in routes:
            print(f"  {route.method} {route.path}")
            total += 1
    print(f"\n总计: {total} 个端点")


def verify(routes_by_module: Dict[str, List[RouteInfo]]):
    """验证模式：对比源码与文档"""
    if not os.path.exists(DOC_PATH):
        print(f"文档不存在: {DOC_PATH}")
        return 1
    
    with open(DOC_PATH, "r", encoding="utf-8") as f:
        doc_content = f.read()
    
    errors = []
    for module_name, routes in routes_by_module.items():
        for route in routes:
            if route.path not in doc_content:
                errors.append(f"缺失接口: {route.method} {route.path}")
    
    if errors:
        print("验证失败！")
        for err in errors:
            print(f"  - {err}")
        return 1
    else:
        print("验证通过！")
        return 0


def main():
    routes_by_module = scan_all_routes()
    
    if "--scaffold" in sys.argv:
        scaffold = generate_scaffold(routes_by_module)
        print(scaffold)
    elif "--scan-only" in sys.argv:
        scan_only(routes_by_module)
    else:
        sys.exit(verify(routes_by_module))


if __name__ == "__main__":
    main()
