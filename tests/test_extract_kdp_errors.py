import tempfile
from pathlib import Path
from scripts.extract_kdp_errors import extract_red_spans


def test_extract_red_spans_style_color_red():
    html = '''
    <p>Hallo <span style="color:red">Abberufbarkeit</span> und 
    <span style="COLOR: RED">Gnadenrecht</span>.</p>
    '''
    result = extract_red_spans(html)
    assert result == ["Abberufbarkeit", "Gnadenrecht"]


def test_extract_red_spans_class_spelling_error():
    html = '''
    <span class="spelling-error">unkippbar</span>
    <span class="error">Rückholmechanik</span>
    <span class="misspelled">Erwirtschaftbare</span>
    '''
    result = extract_red_spans(html)
    assert set(result) == {"unkippbar", "Rückholmechanik", "Erwirtschaftbare"}


def test_extract_red_spans_font_color_red():
    html = '<font color="red">Differential Privacy</font>'
    result = extract_red_spans(html)
    assert result == ["Differential Privacy"]


def test_no_duplicates():
    html = '''
    <span style="color:red">Test</span>
    <span class="error">Test</span>
    '''
    result = extract_red_spans(html)
    assert result == ["Test"]


def test_ignores_empty_and_whitespace():
    html = '''
    <span style="color:red"></span>
    <span style="color:red">  </span>
    <span style="color:red">Wort</span>
    '''
    result = extract_red_spans(html)
    assert result == ["Wort"]


def test_integration_main_script(tmp_path: Path):
    """Simulates full CLI run."""
    input_file = tmp_path / "sample.html"
    input_file.write_text('<span style="color:red">Abberufbarkeit</span>', encoding='utf-8')

    from scripts.extract_kdp_errors import main
    import sys

    original_argv = sys.argv
    try:
        sys.argv = ["extract_kdp_errors", str(input_file)]
        main()
    finally:
        sys.argv = original_argv

    output_file = tmp_path / "sample_kdp_errors.txt"
    assert output_file.exists()
    content = output_file.read_text(encoding='utf-8').strip()
    assert content == "Abberufbarkeit"
