"""Cobre a sanitização do filtro render_md (issue #15).

Antes desta correção o filtro aplicava mark_safe() direto na saída do
Python-Markdown, que não remove HTML bruto. Qualquer marcação escrita no título
ou subtítulo de um slide do carrossel chegava intacta ao navegador.
"""

import pytest

from home.templatetags.markdown_extras import render_md


class TestRenderMdSanitiza:
    @pytest.mark.parametrize(
        "payload",
        [
            "<script>alert(1)</script>",
            '<img src=x onerror="alert(1)">',
            "<svg onload=alert(1)>",
            '<iframe src="//exemplo-externo"></iframe>',
            '<object data="//exemplo-externo"></object>',
            "<style>body{display:none}</style>",
        ],
    )
    def test_remove_tags_fora_da_whitelist(self, payload):
        saida = str(render_md(payload)).lower()
        for marca in ("<script", "<img", "<svg", "<iframe", "<object", "<style"):
            assert marca not in saida

    @pytest.mark.parametrize(
        "payload",
        ['<strong onclick="alert(1)">x</strong>', '<a href="#" onmouseover="alert(1)">x</a>'],
    )
    def test_remove_handlers_de_evento_em_tag_permitida(self, payload):
        saida = str(render_md(payload)).lower()
        assert "onclick" not in saida
        assert "onmouseover" not in saida

    @pytest.mark.parametrize(
        "payload",
        [
            "[clique](javascript:alert(1))",
            '<a href="javascript:alert(1)">x</a>',
            "[x](data:text/html,<script>alert(1)</script>)",
        ],
    )
    def test_bloqueia_protocolos_perigosos(self, payload):
        """Sem restringir protocolos, um link continua sendo vetor de XSS
        mesmo com todas as tags sanitizadas."""
        saida = str(render_md(payload)).lower()
        assert "javascript:" not in saida
        assert "data:text" not in saida

    def test_nao_deixa_passar_href_relativo_malformado(self):
        saida = str(render_md('<a href="  javascript:alert(1)">x</a>')).lower()
        assert "javascript:" not in saida


class TestRenderMdPreservaFormatacao:
    """A sanitização não pode inutilizar o filtro para o uso legítimo."""

    def test_negrito(self):
        assert "<strong>Guitarras</strong>" in str(render_md("**Guitarras** até 30% OFF"))

    def test_italico(self):
        assert "<em>promoção</em>" in str(render_md("*promoção*"))

    def test_link_https_e_mantido(self):
        saida = str(render_md("[loja](https://musicmais.com.br)"))
        assert 'href="https://musicmais.com.br"' in saida

    def test_quebra_de_linha(self):
        assert "<br>" in str(render_md("linha1\nlinha2"))

    def test_texto_puro_atravessa_intacto(self):
        assert "Guitarras em promoção" in str(render_md("Guitarras em promoção"))

    @pytest.mark.parametrize("vazio", ["", None])
    def test_valor_vazio_retorna_string_vazia(self, vazio):
        assert render_md(vazio) == ""
