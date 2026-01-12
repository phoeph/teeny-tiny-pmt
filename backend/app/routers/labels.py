"""
标签树路由：从配置的 Excel 文件解析为树形JSON
"""
from fastapi import APIRouter
from pathlib import Path
from typing import List, Dict, Any
import logging
import time

from app.config import settings

router = APIRouter(prefix="/api/labels", tags=["标签树"])
logger = logging.getLogger(__name__)

_CACHE: Dict[str, Any] | None = None
_CACHE_TIMESTAMP: float = 0


def get_excel_path() -> Path:
    """
    获取 Excel 文件的绝对路径
    支持相对路径和绝对路径配置
    """
    return settings.get_excel_path()


def _excel_path() -> Path:
    """向后兼容的路径获取函数"""
    return get_excel_path()


def _build_tree(rows: List[List[str]]) -> List[Dict[str, Any]]:
    # 逐行构建多级树：每行对应一条路径，如 [一级, 二级, 三级, ...]
    root: Dict[str, Any] = {"children": {}}  # 使用字典构造，最后再转为数组

    def ensure_child(node: Dict[str, Any], name: str) -> Dict[str, Any]:
        ch = node.setdefault("children", {})
        if name not in ch:
            ch[name] = {"name": name, "children": {}}
        return ch[name]

    for r in rows:
        path = [s.strip() for s in r if s and str(s).strip()]
        if not path:
            continue
        cur = root
        for i, name in enumerate(path):
            cur = ensure_child(cur, name)
            if i == len(path) - 1:
                # 叶子：记录完整路径与唯一ID（用路径字符串）
                cur["path"] = "/".join(path)
                cur["id"] = cur["path"]
    # 将字典形式 children 转数组形式
    def dict_to_list(n: Dict[str, Any]) -> List[Dict[str, Any]]:
        arr: List[Dict[str, Any]] = []
        for _, v in (n.get("children") or {}).items():
            node = {"name": v["name"]}
            if "id" in v:
                node["id"] = v["id"]
                node["path"] = v["path"]
            children = dict_to_list(v)
            if children:
                node["children"] = children
            arr.append(node)
        return arr
    return dict_to_list(root)


def _parse_excel() -> List[Dict[str, Any]]:
    from openpyxl import load_workbook
    
    p = _excel_path()
    
    # 文件不存在时返回空列表并记录警告
    if not p.exists():
        logger.warning(f"⚠️  Labels Excel file not found: {p}")
        return []
    
    try:
        wb = load_workbook(filename=str(p), read_only=True, data_only=True)
        ws = wb.active
        rows: List[List[str]] = []
        for row in ws.iter_rows(values_only=True):
            # 每行多个层级（按列），过滤空白
            vals = []
            for c in row:
                if c is None:
                    vals.append("")
                else:
                    vals.append(str(c))
            rows.append(vals)
        
        # 去掉表头（如存在），策略：若首行包含"一级/二级/三级"等字样，则跳过
        if rows:
            header = "/".join([s.strip() for s in rows[0] if s and s.strip()])
            if any(k in header for k in ["一级", "二级", "三级", "四级", "五级", "Level", "层级"]):
                rows = rows[1:]
        
        logger.info(f"✅ Successfully parsed Excel file: {p}")
        return _build_tree(rows)
    
    except Exception as e:
        logger.error(f"❌ Error parsing Excel file {p}: {e}")
        return []


def get_label_tree_data(force_reload: bool = False) -> Dict[str, Any]:
    """
    获取标签树数据，支持缓存和强制刷新
    
    Args:
        force_reload: 是否强制重新加载
    
    Returns:
        包含标签树的字典
    """
    global _CACHE, _CACHE_TIMESTAMP
    
    excel_path = get_excel_path()
    
    # 检查文件修改时间
    if excel_path.exists():
        file_mtime = excel_path.stat().st_mtime
        
        # 如果强制刷新，或缓存为空，或文件已更新，则重新加载
        if force_reload or _CACHE is None or file_mtime > _CACHE_TIMESTAMP:
            logger.info(f"🔄 Reloading labels from Excel file: {excel_path}")
            _CACHE = {"items": _parse_excel()}
            _CACHE_TIMESTAMP = file_mtime
    else:
        # 文件不存在，返回空标签树
        logger.warning(f"⚠️  Labels Excel file not found: {excel_path}")
        if _CACHE is None:
            _CACHE = {"items": []}
    
    return _CACHE


@router.get("/tree")
async def get_label_tree():
    """获取标签树"""
    return get_label_tree_data(force_reload=False)


@router.post("/tree/reload")
async def reload_label_tree():
    """手动触发标签树重新加载"""
    logger.info("🔄 Manual reload triggered for labels tree")
    get_label_tree_data(force_reload=True)
    return {"message": "Label tree reloaded successfully", "status": "ok"}
