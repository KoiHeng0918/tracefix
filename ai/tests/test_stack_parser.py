from parsers.stack_parser import (
    extract_exception,
    extract_message,
    fingerprint,
)


def test_extract_exception():
    trace = "java.sql.SQLException: Access denied for user 'root'@'localhost'"

    assert extract_exception(trace) == "java.sql.SQLException"


def test_extract_exception_unknown():
    assert extract_exception("just a plain message") == "UNKNOWN"
    assert extract_exception(None) == "UNKNOWN"


def test_extract_message_normalizes_unstable_parts():
    trace = (
        r"java.sql.SQLException: User 9527 failed at D:\project\src\UserService.java "
        r"request 550e8400-e29b-41d4-a716-446655440000 address 0x7ffee3a"
        "\n\tat com.demo.UserService.login(UserService.java:42)"
    )

    assert extract_message(trace) == (
        "java.sql.SQLException: User {id} failed at {path} "
        "request {uuid} address {hex}"
    )


def test_extract_message_uses_first_line_only():
    trace = "java.sql.SQLException: first line\nsecond line 1234"

    assert extract_message(trace) == "java.sql.SQLException: first line"


def test_fingerprint_is_stable():
    message = extract_message(
        "java.sql.SQLException: User 9527 not found"
    )

    fp1 = fingerprint("java.sql.SQLException", message, "")
    fp2 = fingerprint("java.sql.SQLException", message, "")

    assert fp1 == fp2
    assert len(fp1) == 64
    assert all(char in "0123456789abcdef" for char in fp1)


def test_fingerprint_changes_with_exception():
    message = "Access denied"

    fp1 = fingerprint("java.sql.SQLException", message, "")
    fp2 = fingerprint("java.lang.NullPointerException", message, "")

    assert fp1 != fp2
