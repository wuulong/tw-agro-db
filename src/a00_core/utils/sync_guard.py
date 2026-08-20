"""
src/a00_core/utils/sync_guard.py
全庫通用智慧同步防護器 (Smart Sync Guard)
支援 HTTP ETag/Last-Modified 標頭檢查與檔案 SHA-256 位元組 MD5/SHA256 Hash 智慧跳過機制
"""
import hashlib
import json
from pathlib import Path
from typing import Union, Dict, Any, Tuple, Optional
import urllib.request
import urllib.error

def compute_file_sha256(file_path: Union[str, Path]) -> str:
    """計算檔案 SHA-256 Hash"""
    p = Path(file_path)
    if not p.exists():
        return ""
    hasher = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def check_remote_header_modified(url: str, etag: str = "", last_modified: str = "") -> Tuple[bool, Dict[str, str]]:
    """
    發送 HTTP HEAD 請求檢查遠端檔案 ETag / Last-Modified 標頭
    返回 (是否有變更, 標頭資訊)
    """
    headers = {"User-Agent": "tw-agro-db Smart Sync Guard/1.0"}
    if etag:
        headers["If-None-Match"] = etag
    if last_modified:
        headers["If-Modified-Since"] = last_modified
        
    req = urllib.request.Request(url, headers=headers, method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            res_etag = response.headers.get("ETag", "").strip('"')
            res_lm = response.headers.get("Last-Modified", "")
            return True, {"etag": res_etag, "last_modified": res_lm}
    except urllib.error.HTTPError as e:
        if e.code == 304:
            # 遠端未修改 ➔ 智慧跳過
            return False, {"etag": etag, "last_modified": last_modified}
        return True, {}
    except Exception:
        # 連線失敗或不支援 HEAD 請求時，保守策略返回有變更，交由 Hash 關卡攔截
        return True, {}

def should_skip_etl_by_hash(
    new_json_path: Union[str, Path],
    metadata_json_path: Union[str, Path]
) -> Tuple[bool, str, str]:
    """
    發動 2 階 Content Hash 智慧比對
    返回 (是否跳過, 新計算Hash, 理由)
    """
    json_p = Path(new_json_path)
    meta_p = Path(metadata_json_path)
    
    if not json_p.exists():
        return False, "", "來源 JSON 檔案不存在，無法跳過"
        
    new_hash = compute_file_sha256(json_p)
    
    if meta_p.exists():
        try:
            meta = json.loads(meta_p.read_text(encoding="utf-8"))
            old_hash = meta.get("data_source", {}).get("sha256_hash", "")
            if old_hash and old_hash == new_hash:
                return True, new_hash, f"⚡ 內容 SHA-256 Hash 一致 ({new_hash[:8]}...)，智慧跳過重覆 ETL 入庫！"
        except Exception:
            pass
            
    return False, new_hash, "資料內容有變更，執行增量 ETL 入庫"
