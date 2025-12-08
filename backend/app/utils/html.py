import re

ALLOWED_TAGS = set([
    'p','br','h1','h2','h3','h4','h5','h6','b','i','u','strong','em',
    'ul','ol','li','blockquote','code','pre','span','a','img','table','thead','tbody','tr','td','th'
])
ALLOWED_ATTRS = {
    'a': {'href','title','target','rel'},
    'img': {'src','alt','width','height'},
    'span': {'style'},
    'p': {'style'},
    'h1': {'style'}, 'h2': {'style'}, 'h3': {'style'}, 'h4': {'style'}, 'h5': {'style'}, 'h6': {'style'},
    'code': set(), 'pre': set(), 'blockquote': set(), 'ul': set(), 'ol': set(), 'li': set(),
    'table': {'border','cellpadding','cellspacing','style'}, 'tr': set(), 'td': {'colspan','rowspan','style'}, 'th': {'colspan','rowspan','style'},
}

SCRIPT_PATTERN = re.compile(r"<\s*(script|iframe|embed|object)[^>]*>.*?<\s*/\s*\1\s*>", re.IGNORECASE|re.DOTALL)
ON_ATTR_PATTERN = re.compile(r"\s(on[a-z]+)\s*=\s*\"[^\"]*\"", re.IGNORECASE)

def sanitize_html(html: str) -> str:
    if not html:
        return ''
    s = str(html)
    # 移除危险标签块
    s = SCRIPT_PATTERN.sub('', s)
    # 移除 on* 内联事件
    s = ON_ATTR_PATTERN.sub('', s)
    # 粗略白名单：剔除不允许的标签（保留标签内容）
    def strip_unallowed_tags(text: str) -> str:
        return re.sub(r"<\s*/?\s*([a-zA-Z0-9]+)([^>]*)>", lambda m: _filter_tag(m.group(0), m.group(1), m.group(2)), text)
    def _filter_tag(full: str, tag: str, attrs: str) -> str:
        t = tag.lower()
        if t in ALLOWED_TAGS:
            # 过滤属性，仅保留允许属性键
            allowed = ALLOWED_ATTRS.get(t, set())
            kept = []
            for kv in re.findall(r"([a-zA-Z0-9:-]+)\s*=\s*\"([^\"]*)\"", attrs or ''):
                k, v = kv
                k = k.lower()
                if k in allowed:
                    # href 限制协议
                    if t == 'a' and k == 'href' and (not re.match(r"^(https?:|mailto:|#)", v)):
                        continue
                    kept.append(f" {k}=\"{v}\"")
            if full.strip().startswith("</"):
                return f"</{t}>"
            return f"<{t}{''.join(kept)}>"
        # 非白名单：去掉标签，仅保留文本（粗略处理）
        return ''
    s = strip_unallowed_tags(s)
    return s
