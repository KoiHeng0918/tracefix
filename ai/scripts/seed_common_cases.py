import sys
from pathlib import Path

# 让脚本在 ai/scripts 下运行时也能 import ai/ 下的模块
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from parsers.stack_parser import fingerprint
from retrieval.case_repository import get_connection


CASES = [
    {
        "case_no": "ERR-SPRING-0004",
        "title": "唯一键冲突导致 DuplicateKeyException",
        "category": "spring",
        "exception_type": "org.springframework.dao.DuplicateKeyException",
        "message_pattern": "Duplicate entry '{value}' for key '{index}'",
        "tech_stack": "Spring Boot 3.x + MyBatis-Plus",
        "version_scope": "未验证",
        "symptom": "插入或更新数据时数据库返回唯一键冲突，Spring 转换为 DuplicateKeyException。",
        "root_cause": "插入的数据违反了数据库唯一索引，通常是重复提交、幂等未处理或业务唯一约束冲突。",
        "fix_steps": "1. 从异常消息确认冲突字段；2. 查询数据库是否已存在；3. 增加唯一性预检查或幂等键；4. 必要时捕获异常转换为业务提示。",
        "verification": "同一业务键重复提交不再产生未处理异常，接口返回明确的重复提示。",
        "source": "公开常见错误整理",
    },
    {
        "case_no": "ERR-MYSQL-0003",
        "title": "数据库表不存在导致 SQLSyntaxErrorException",
        "category": "mysql",
        "exception_type": "java.sql.SQLSyntaxErrorException",
        "message_pattern": "Table '{database}.{table}' doesn't exist",
        "tech_stack": "MySQL 8.x + MyBatis",
        "version_scope": "未验证",
        "symptom": "执行 SQL 时提示表不存在，应用接口返回数据库异常。",
        "root_cause": "数据库未执行建表脚本、连接到了错误的库、表名大小写不一致，或环境配置没有同步。",
        "fix_steps": "1. 确认当前连接的数据库；2. 检查表是否已创建；3. 执行建表或迁移脚本；4. 检查表名大小写和配置。",
        "verification": "查询接口正常返回，数据库中能看到对应表。",
        "source": "公开常见错误整理",
    },
    {
        "case_no": "ERR-MYSQL-0004",
        "title": "并发更新导致 MySQL 死锁",
        "category": "mysql",
        "exception_type": "com.mysql.cj.jdbc.exceptions.MySQLTransactionRollbackException",
        "message_pattern": "Deadlock found when trying to get lock; try restarting transaction",
        "tech_stack": "MySQL 8.x + Spring Transaction",
        "version_scope": "未验证",
        "symptom": "并发更新时事务被数据库回滚，日志提示死锁。",
        "root_cause": "多个事务以不同顺序锁定相同行或索引，形成循环等待。",
        "fix_steps": "1. 查看 InnoDB 死锁日志；2. 统一加锁顺序；3. 缩短事务范围；4. 对可重试业务增加重试。",
        "verification": "并发压测下死锁明显减少，事务能正常提交或按策略重试。",
        "source": "公开常见错误整理",
    },
    {
        "case_no": "ERR-MYBATIS-0002",
        "title": "Mapper 参数名不匹配导致 BindingException",
        "category": "mybatis",
        "exception_type": "org.apache.ibatis.binding.BindingException",
        "message_pattern": "Parameter '{name}' not found. Available parameters are [{list}]",
        "tech_stack": "MyBatis 3.x + Spring Boot",
        "version_scope": "未验证",
        "symptom": "调用 Mapper 方法时提示参数名不存在，SQL 无法绑定参数。",
        "root_cause": "Mapper 方法参数没有使用 @Param，XML 中引用了不存在的参数名，或编译时没有保留参数名。",
        "fix_steps": "1. 检查 Mapper 方法参数；2. 多参数使用 @Param；3. XML 中使用正确参数名；4. 重新编译并重启。",
        "verification": "Mapper 方法调用成功，XML 能正确绑定参数。",
        "source": "公开常见错误整理",
    },
    {
        "case_no": "ERR-JAVA-0005",
        "title": "遍历集合时修改导致 ConcurrentModificationException",
        "category": "jvm",
        "exception_type": "java.util.ConcurrentModificationException",
        "message_pattern": "ConcurrentModificationException",
        "tech_stack": "Java 17",
        "version_scope": "未验证",
        "symptom": "遍历集合时修改集合，抛出 ConcurrentModificationException。",
        "root_cause": "使用 for-each 遍历集合时直接 add/remove，导致迭代器检测到结构修改。",
        "fix_steps": "1. 使用 Iterator.remove；2. 收集后批量删除；3. 使用并发集合或复制集合；4. 避免遍历中修改。",
        "verification": "相同场景不再抛异常，集合修改结果符合预期。",
        "source": "公开常见错误整理",
    },
]


def main():
    with get_connection() as conn:
        with conn.cursor() as cur:
            inserted = 0
            for case in CASES:
                cur.execute(
                    "SELECT case_no FROM qa_error_case WHERE case_no = %s",
                    (case["case_no"],),
                )
                if cur.fetchone():
                    print("skip existing:", case["case_no"])
                    continue

                fp = fingerprint(
                    case["exception_type"],
                    case["message_pattern"],
                    "",
                )
                cur.execute(
                    """
                    INSERT INTO qa_error_case
                    (case_no, title, category, exception_type, message_pattern,
                     tech_stack, version_scope, symptom, root_cause, fix_steps,
                     verification, source, fingerprint, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'ACTIVE')
                    """,
                    (
                        case["case_no"], case["title"], case["category"],
                        case["exception_type"], case["message_pattern"],
                        case["tech_stack"], case["version_scope"], case["symptom"],
                        case["root_cause"], case["fix_steps"], case["verification"],
                        case["source"], fp,
                    ),
                )
                inserted += 1
                print("inserted:", case["case_no"], case["title"])
        conn.commit()
    print("total inserted:", inserted)


if __name__ == "__main__":
    main()
