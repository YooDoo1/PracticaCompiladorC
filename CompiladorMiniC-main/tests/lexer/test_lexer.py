"""Pruebas del analizador léxico de Mini C según SKILL.md."""

import pytest

from minic.diagnostics import diagnostic_code
from minic.lexer.lexer import Lexer
from minic.lexer.token_type import TokenType
from minic.output.diagnostic_printer import format_diagnostic
from minic.output.token_printer import format_token


def test_section_7_case_1_valid() -> None:
    source = "int2 = 12abc;\nwhilex == -5"
    tokens, diagnostics = Lexer(source).scan()

    assert diagnostics == []

    formatted = [format_token(t) for t in tokens]
    expected = [
        "IDENTIFIER 'int2' 1 1",
        "ASSIGN '=' 1 6",
        "INTEGER_LITERAL '12' 1 8",
        "IDENTIFIER 'abc' 1 10",
        "SEMICOLON ';' 1 13",
        "IDENTIFIER 'whilex' 2 1",
        "EQUAL_EQUAL '==' 2 8",
        "MINUS '-' 2 11",
        "INTEGER_LITERAL '5' 2 12",
        "EOF '' 2 13",
    ]
    assert formatted == expected
    assert tokens[2].literal == 12
    assert tokens[8].literal == 5


def test_section_7_case_2_with_errors() -> None:
    source = "int x = @;\nx ! = 0; // fin"
    tokens, diagnostics = Lexer(source).scan()

    formatted_tokens = [format_token(t) for t in tokens]
    expected_tokens = [
        "KW_INT 'int' 1 1",
        "IDENTIFIER 'x' 1 5",
        "ASSIGN '=' 1 7",
        "SEMICOLON ';' 1 10",
        "IDENTIFIER 'x' 2 1",
        "ASSIGN '=' 2 5",
        "INTEGER_LITERAL '0' 2 7",
        "SEMICOLON ';' 2 8",
        "IDENTIFIER 'fin' 2 13",
        "EOF '' 2 16",
    ]
    assert formatted_tokens == expected_tokens

    formatted_diagnostics = [format_diagnostic(d) for d in diagnostics]
    expected_diagnostics = [
        "LEX001 error 1:9 Carácter no reconocido: '@'",
        "LEX001 error 2:3 Carácter no reconocido: '!'",
        "LEX001 error 2:10 Carácter no reconocido: '/'",
        "LEX001 error 2:11 Carácter no reconocido: '/'",
    ]
    assert formatted_diagnostics == expected_diagnostics


def test_all_single_and_double_tokens() -> None:
    source = "+ - == != = ( ) { } ;"
    tokens, diagnostics = Lexer(source).scan()
    assert diagnostics == []
    types = [t.type for t in tokens]
    assert types == [
        TokenType.PLUS,
        TokenType.MINUS,
        TokenType.EQUAL_EQUAL,
        TokenType.NOT_EQUAL,
        TokenType.ASSIGN,
        TokenType.LPAREN,
        TokenType.RPAREN,
        TokenType.LBRACE,
        TokenType.RBRACE,
        TokenType.SEMICOLON,
        TokenType.EOF,
    ]


def test_keywords_and_identifiers() -> None:
    source = "int while int_var while1 _abc ABC"
    tokens, diagnostics = Lexer(source).scan()
    assert diagnostics == []
    expected = [
        (TokenType.KW_INT, "int"),
        (TokenType.KW_WHILE, "while"),
        (TokenType.IDENTIFIER, "int_var"),
        (TokenType.IDENTIFIER, "while1"),
        (TokenType.IDENTIFIER, "_abc"),
        (TokenType.IDENTIFIER, "ABC"),
        (TokenType.EOF, ""),
    ]
    assert [(t.type, t.lexeme) for t in tokens] == expected


def test_integer_literal_values() -> None:
    source = "0 007 12345"
    tokens, diagnostics = Lexer(source).scan()
    assert diagnostics == []
    assert tokens[0].literal == 0
    assert tokens[1].literal == 7
    assert tokens[2].literal == 12345


def test_whitespace_and_positions() -> None:
    # \t is 1 column, \r is 1 column, \n increments line and resets column to 1
    source = "\t\r\nx"
    tokens, diagnostics = Lexer(source).scan()
    assert diagnostics == []
    assert len(tokens) == 2
    tok_x = tokens[0]
    assert tok_x.type == TokenType.IDENTIFIER
    assert tok_x.lexeme == "x"
    assert tok_x.line == 2
    assert tok_x.column == 1


def test_empty_source() -> None:
    tokens, diagnostics = Lexer("").scan()
    assert diagnostics == []
    assert len(tokens) == 1
    assert tokens[0].type == TokenType.EOF
    assert tokens[0].lexeme == ""
    assert tokens[0].line == 1
    assert tokens[0].column == 1
