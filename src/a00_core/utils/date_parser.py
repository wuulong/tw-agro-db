import re
from typing import Optional

def parse_roc_date_universal(raw_val: Optional[str]) -> str:
    """
    全能民國年/西元年萬用日期解析器
    支援格式:
      - '115.08.19' -> '2026-08-19' (點號分隔)
      - '0771012'   -> '1988-10-12' (7碼無斜線)
      - '079/05/03' -> '1990-05-03' (斜線分隔)
      - '1150819'   -> '2026-08-19' (7碼無槓)
      - '2026-08-19' -> '2026-08-19' (已為西元年)
    """
    if not raw_val:
        return ""
        
    s = str(raw_val).strip()
    
    # 格式 1: 已為西元年 YYYY-MM-DD
    if re.match(r"^\d{4}-\d{2}-\d{2}$", s):
        return s
        
    # 格式 2: 點號或斜線分隔 (如 115.08.19 或 079/05/03 或 115/8/19)
    m_sep = re.match(r"^(\d{2,3})[./](\d{1,2})[./](\d{1,2})$", s)
    if m_sep:
        roc_y, m, d = m_sep.groups()
        y = int(roc_y) + 1911
        return f"{y:04d}-{int(m):02d}-{int(d):02d}"
        
    # 格式 3: 緊密 7 碼純數字 (如 0771012 或 1150819)
    if len(s) == 7 and s.isdigit():
        y = int(s[:3]) + 1911
        m = s[3:5]
        d = s[5:7]
        return f"{y:04d}-{m}-{d}"
        
    # 格式 4: 緊密 6 碼純數字 (如 771012)
    if len(s) == 6 and s.isdigit():
        y = int(s[:2]) + 1911
        m = s[2:4]
        d = s[4:6]
        return f"{y:04d}-{m}-{d}"
        
    return s
