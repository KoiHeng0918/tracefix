import hashlib
import re


# 匹配"带包名的异常类"：如java.sql.SQLException
EXCEPTION_RE = re.compile(r"([a-zA-Z_$][\w$]*(?:\.[a-zA-Z_$][\w$]*)+(?:Exception|Error))")

# 匹配 UUID：如550e8400-e29b-41d4-a716-446655440000
UUID_RE = re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b")

# 匹配文件路径：
# Windows：D:\project\src\UserService.java
# Linux/Mac：/home/user/project/UserService.java
PATH_RE = re.compile(r"([A-Za-z]:\\[^\s:]+|/(?:[\w.-]+/)+[\w.-]+)")

# 匹配十六进制数：如0x7ffee3a
HEX_RE = re.compile(r"0x[0-9a-fA-F]+")

# 匹配连续 4 位以上的数字：如用户 ID、订单号、时间戳
LONG_NUMBER_RE = re.compile(r"\b\d{4,}\b")


# 大致都分为,1拆分,2匹配,3返回结果


def extract_exception(trace: str) -> str:
    """从报错文本里找第一个异常类名，找不到就返回 UNKNOWN。"""
    # 1. 匹配
    # trace 可能是 None，所以用 trace or "" 兜底成空字符串
    # search全文获取对应信息
    match = EXCEPTION_RE.search(trace or "")


    # 2. 返回
    # group(1) 表示取正则里第一个括号匹配到的内容，也就是异常类名
    # 没匹配到就返回UNKOWN
    return match.group(1) if match else "UNKNOWN"


def extract_message(trace: str) -> str:
    """把异常消息里不稳定的内容替换成占位符，方便生成稳定指纹。"""
    text = trace or ""

    # 1. 拆分
    # 只取第一行，避免把整段堆栈都塞进消息
    first = text.splitlines()[0] if text else ""


    # 2. 匹配
    # 用正则编译后的sub方法，把不稳定的内容替换成固定占位符
    first = UUID_RE.sub("{uuid}", first)
    first = PATH_RE.sub("{path}", first)
    first = HEX_RE.sub("{hex}", first)
    first = LONG_NUMBER_RE.sub("{id}", first)

    # 把连续空白（空格、换行、制表符）压成一个空格，并去掉首尾空格
    return re.sub(r"\s+", " ", first).strip()


def fingerprint(exception: str, message: str, error_code: str = "") -> str:
    """把异常类型、归一化消息和错误码拼起来，生成 SHA-256 指纹。"""
    # 用 | 分隔各个部分，方便以后调整格式时升级版本号
    payload = "v1|{}|{}|{}".format(
        exception or "UNKNOWN",
        message or "",
        error_code or "",
    )

    # encode("utf-8") 把字符串转成字节
    # 使用hashlib的sha256 对字节做哈希
    # hexdigest() 把哈希结果转成十六进制字符串
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
