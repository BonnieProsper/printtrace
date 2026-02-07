from printtrace.api import printtrace


def test_output_not_truncated_at_exit(capture_output):
    writer, get_lines = capture_output

    for i in range(100):
        printtrace("line", i, file=writer, mode="minimal")


    output = get_lines()

    assert len(output) == 100
    assert output[0].startswith("line 0")
    assert output[-1].startswith("line 99")


def test_immediate_exit_pattern(capture_output):
    writer, get_lines = capture_output

    printtrace("last line", file=writer)

    output = get_lines()

    assert len(output) == 1
    assert output[0].endswith("last line")
