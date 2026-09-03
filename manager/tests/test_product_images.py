import io

import pytest
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from faker import Faker
from PIL import Image

from catalog.models import Instrument, ProductImage

fake = Faker("pt_BR")


def png_bytes(tamanho=(1, 1)):
    """Gera um PNG real.

    O fixture anterior era uma sequência de bytes fixa com CRC inválido no chunk
    IDAT — o Pillow a rejeita. Nunca foi notado porque a view criava ProductImage
    com objects.create(), que não valida nada. Com a validação no servidor
    (issue #16), o fixture precisa ser uma imagem de verdade.
    """
    buffer = io.BytesIO()
    Image.new("RGB", tamanho, "red").save(buffer, format="PNG")
    return buffer.getvalue()


def make_image(nome=None):
    return SimpleUploadedFile(
        nome or f"{fake.slug()}.png",
        png_bytes(),
        content_type="image/png",
    )


@pytest.fixture(autouse=True)
def use_tmp_media(tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path


@pytest.fixture
def staff_user(db):
    return User.objects.create_user(
        username=fake.user_name(),
        password=fake.password(),
        is_staff=True,
    )


@pytest.fixture
def regular_user(db):
    return User.objects.create_user(
        username=fake.user_name(),
        password=fake.password(),
        is_staff=False,
    )


@pytest.fixture
def product_image(db, instrument):
    return ProductImage.objects.create(
        instrument=instrument,
        image=make_image(),
        is_main=True,
        order=0,
    )


class TestProductImageUploadView:
    def test_upload_single_image_saves_and_redirects(self, client, staff_user, instrument):
        client.force_login(staff_user)
        response = client.post(
            reverse("manager:product_image_upload", kwargs={"pk": instrument.pk}),
            {"images": make_image()},
        )
        assert response.status_code == 302
        assert instrument.images.count() == 1

    def test_redirect_goes_to_product_update_page(self, client, staff_user, instrument):
        client.force_login(staff_user)
        response = client.post(
            reverse("manager:product_image_upload", kwargs={"pk": instrument.pk}),
            {"images": make_image()},
        )
        assert response["Location"] == reverse("manager:inventory_update", kwargs={"pk": instrument.pk})

    def test_first_uploaded_image_becomes_main(self, client, staff_user, instrument):
        client.force_login(staff_user)
        client.post(
            reverse("manager:product_image_upload", kwargs={"pk": instrument.pk}),
            {"images": make_image()},
        )
        assert instrument.images.filter(is_main=True).count() == 1

    def test_upload_multiple_images(self, client, staff_user, instrument):
        client.force_login(staff_user)
        response = client.post(
            reverse("manager:product_image_upload", kwargs={"pk": instrument.pk}),
            {"images": [make_image() for _ in range(3)]},
        )
        assert response.status_code == 302
        assert instrument.images.count() == 3

    def test_respects_max_5_limit(self, client, staff_user, instrument):
        client.force_login(staff_user)
        for i in range(3):
            ProductImage.objects.create(instrument=instrument, image=make_image(), order=i)
        client.post(
            reverse("manager:product_image_upload", kwargs={"pk": instrument.pk}),
            {"images": [make_image() for _ in range(4)]},
        )
        assert instrument.images.count() == 5

    def test_upload_when_at_max_does_not_add_images(self, client, staff_user, instrument):
        client.force_login(staff_user)
        for i in range(5):
            ProductImage.objects.create(instrument=instrument, image=make_image(), order=i)
        response = client.post(
            reverse("manager:product_image_upload", kwargs={"pk": instrument.pk}),
            {"images": make_image()},
        )
        assert response.status_code == 302
        assert instrument.images.count() == 5

    def test_subsequent_upload_does_not_override_main(self, client, staff_user, instrument):
        client.force_login(staff_user)
        ProductImage.objects.create(instrument=instrument, image=make_image(), is_main=True, order=0)
        client.post(
            reverse("manager:product_image_upload", kwargs={"pk": instrument.pk}),
            {"images": make_image()},
        )
        assert instrument.images.filter(is_main=True).count() == 1

    def test_no_files_redirects_without_saving(self, client, staff_user, instrument):
        client.force_login(staff_user)
        response = client.post(
            reverse("manager:product_image_upload", kwargs={"pk": instrument.pk}),
            {},
        )
        assert response.status_code == 302
        assert instrument.images.count() == 0

    def test_requires_staff(self, client, regular_user, instrument):
        client.force_login(regular_user)
        response = client.post(
            reverse("manager:product_image_upload", kwargs={"pk": instrument.pk}),
            {"images": make_image()},
        )
        assert response.status_code == 302
        assert instrument.images.count() == 0


HTMX_HEADERS = {"HTTP_HX_REQUEST": "true"}


class TestProductImageDeleteView:
    def test_htmx_delete_returns_partial(self, client, staff_user, product_image, instrument):
        client.force_login(staff_user)
        pk = product_image.pk
        response = client.post(
            reverse("manager:product_image_delete", kwargs={"image_pk": pk}),
            **HTMX_HEADERS,
        )
        assert response.status_code == 200
        assert not ProductImage.objects.filter(pk=pk).exists()

    def test_non_htmx_delete_redirects(self, client, staff_user, product_image, instrument):
        client.force_login(staff_user)
        pk = product_image.pk
        response = client.post(
            reverse("manager:product_image_delete", kwargs={"image_pk": pk})
        )
        assert response.status_code == 302
        assert not ProductImage.objects.filter(pk=pk).exists()

    def test_missing_image_htmx_returns_204(self, client, staff_user):
        client.force_login(staff_user)
        response = client.post(
            reverse("manager:product_image_delete", kwargs={"image_pk": 99999}),
            **HTMX_HEADERS,
        )
        assert response.status_code == 204

    def test_deleting_main_promotes_next_by_order(self, client, staff_user, instrument):
        client.force_login(staff_user)
        main_img = ProductImage.objects.create(instrument=instrument, image=make_image(), is_main=True, order=0)
        other_img = ProductImage.objects.create(instrument=instrument, image=make_image(), is_main=False, order=1)
        client.post(
            reverse("manager:product_image_delete", kwargs={"image_pk": main_img.pk}),
            **HTMX_HEADERS,
        )
        other_img.refresh_from_db()
        assert other_img.is_main is True

    def test_deleting_non_main_preserves_main(self, client, staff_user, instrument):
        client.force_login(staff_user)
        main_img = ProductImage.objects.create(instrument=instrument, image=make_image(), is_main=True, order=0)
        other_img = ProductImage.objects.create(instrument=instrument, image=make_image(), is_main=False, order=1)
        client.post(
            reverse("manager:product_image_delete", kwargs={"image_pk": other_img.pk}),
            **HTMX_HEADERS,
        )
        main_img.refresh_from_db()
        assert main_img.is_main is True

    def test_deleting_last_image_leaves_no_main(self, client, staff_user, instrument):
        client.force_login(staff_user)
        only_img = ProductImage.objects.create(instrument=instrument, image=make_image(), is_main=True, order=0)
        client.post(
            reverse("manager:product_image_delete", kwargs={"image_pk": only_img.pk}),
            **HTMX_HEADERS,
        )
        assert instrument.images.count() == 0

    def test_requires_staff(self, client, regular_user, product_image):
        client.force_login(regular_user)
        response = client.post(
            reverse("manager:product_image_delete", kwargs={"image_pk": product_image.pk}),
            **HTMX_HEADERS,
        )
        assert response.status_code == 302
        assert ProductImage.objects.filter(pk=product_image.pk).exists()


class TestProductImageSetMainView:
    def test_htmx_set_main_returns_partial(self, client, staff_user, instrument):
        client.force_login(staff_user)
        img1 = ProductImage.objects.create(instrument=instrument, image=make_image(), is_main=True, order=0)
        img2 = ProductImage.objects.create(instrument=instrument, image=make_image(), is_main=False, order=1)
        response = client.post(
            reverse("manager:product_image_set_main", kwargs={"image_pk": img2.pk}),
            **HTMX_HEADERS,
        )
        assert response.status_code == 200
        img1.refresh_from_db()
        img2.refresh_from_db()
        assert img2.is_main is True
        assert img1.is_main is False

    def test_non_htmx_set_main_redirects(self, client, staff_user, instrument):
        client.force_login(staff_user)
        img = ProductImage.objects.create(instrument=instrument, image=make_image(), is_main=False, order=0)
        response = client.post(
            reverse("manager:product_image_set_main", kwargs={"image_pk": img.pk})
        )
        assert response.status_code == 302

    def test_missing_image_htmx_returns_204(self, client, staff_user):
        client.force_login(staff_user)
        response = client.post(
            reverse("manager:product_image_set_main", kwargs={"image_pk": 99999}),
            **HTMX_HEADERS,
        )
        assert response.status_code == 204

    def test_only_one_image_is_main(self, client, staff_user, instrument):
        client.force_login(staff_user)
        images = [
            ProductImage.objects.create(instrument=instrument, image=make_image(), is_main=(i == 0), order=i)
            for i in range(3)
        ]
        client.post(
            reverse("manager:product_image_set_main", kwargs={"image_pk": images[2].pk}),
            **HTMX_HEADERS,
        )
        assert instrument.images.filter(is_main=True).count() == 1

    def test_requires_staff(self, client, regular_user, product_image):
        client.force_login(regular_user)
        response = client.post(
            reverse("manager:product_image_set_main", kwargs={"image_pk": product_image.pk}),
            **HTMX_HEADERS,
        )
        assert response.status_code == 302


class TestProductImageValidacaoServidor:
    """Cobre a validação de upload no servidor (issue #16).

    A view criava ProductImage com objects.create(), que não chama full_clean():
    nada era validado no servidor. A filtragem por tipo existia apenas no
    componente Alpine do template, que qualquer cliente HTTP ignora.
    """

    def _form(self, nome, conteudo, content_type="image/png"):
        from manager.forms import ProductImageForm

        arquivo = SimpleUploadedFile(nome, conteudo, content_type=content_type)
        return ProductImageForm(files={"image": arquivo})

    def test_aceita_png_valido(self):
        assert self._form("foto.png", png_bytes()).is_valid()

    @pytest.mark.parametrize("extensao", ["jpg", "webp"])
    def test_aceita_demais_formatos_web(self, extensao):
        import io

        buffer = io.BytesIO()
        formato = "JPEG" if extensao == "jpg" else "WEBP"
        Image.new("RGB", (2, 2), "red").save(buffer, format=formato)
        assert self._form(f"foto.{extensao}", buffer.getvalue()).is_valid()

    def test_rejeita_svg_com_script(self):
        svg = b'<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>'
        assert not self._form("x.svg", svg, "image/svg+xml").is_valid()

    def test_rejeita_svg_renomeado_para_png(self):
        """Renomear não engana: quem valida é o Pillow, não a extensão."""
        svg = b'<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>'
        assert not self._form("disfarce.png", svg).is_valid()

    def test_rejeita_html_renomeado_para_png(self):
        assert not self._form("e.png", b"<html><script>alert(1)</script></html>").is_valid()

    def test_rejeita_content_type_mentiroso_mas_aceita_bytes_validos(self):
        """content-type vem do cliente e não é confiável em nenhuma direção:
        o que decide é o conteúdo real do arquivo."""
        assert self._form("ok.png", png_bytes(), content_type="text/html").is_valid()

    @pytest.mark.parametrize("extensao", ["bmp", "tiff"])
    def test_rejeita_formato_de_imagem_fora_da_whitelist(self, extensao):
        """São imagens válidas para o Pillow, mas não são formatos web."""
        import io

        buffer = io.BytesIO()
        Image.new("RGB", (2, 2), "red").save(buffer, format=extensao.upper())
        form = self._form(f"f.{extensao}", buffer.getvalue())
        assert not form.is_valid()
        assert "não aceita" in str(form.errors["image"])

    def test_rejeita_arquivo_acima_do_limite(self):
        from manager.forms import ProductImageForm

        excedente = b"\x00" * (ProductImageForm.MAX_UPLOAD_SIZE + 1)
        form = self._form("g.png", png_bytes() + excedente)
        assert not form.is_valid()
        assert "excede o limite" in str(form.errors["image"])

    def test_limite_de_tamanho_e_configuravel(self):
        from manager.forms import ProductImageForm

        assert isinstance(ProductImageForm.MAX_UPLOAD_SIZE, int)
        assert ProductImageForm.EXTENSOES_ACEITAS == {"jpg", "jpeg", "png", "webp"}


@pytest.mark.django_db
class TestUploadViewRejeitaArquivoInvalido:
    """A validação precisa valer no endpoint, não só no form isolado."""

    def _post(self, client, instrument, arquivos):
        return client.post(
            reverse("manager:product_image_upload", args=[instrument.pk]),
            {"images": arquivos},
            follow=True,
        )

    def test_arquivo_nao_imagem_nao_cria_registro(self, client, staff_user, instrument):
        client.force_login(staff_user)
        malicioso = SimpleUploadedFile(
            "payload.png", b"<html><script>alert(1)</script></html>", content_type="image/png"
        )
        self._post(client, instrument, [malicioso])
        assert instrument.images.count() == 0

    def test_arquivo_valido_no_meio_de_invalidos_e_salvo(self, client, staff_user, instrument):
        client.force_login(staff_user)
        arquivos = [
            SimpleUploadedFile("ruim.png", b"nao sou imagem", content_type="image/png"),
            make_image("boa.png"),
        ]
        self._post(client, instrument, arquivos)
        assert instrument.images.count() == 1

    def test_usuario_ve_o_motivo_da_rejeicao(self, client, staff_user, instrument):
        client.force_login(staff_user)
        ruim = SimpleUploadedFile("ruim.png", b"nao sou imagem", content_type="image/png")
        resposta = self._post(client, instrument, [ruim])
        mensagens = [m.message for m in resposta.context["messages"]]
        assert any("ruim.png" in m for m in mensagens)
