from django.core.exceptions import ValidationError
from django.db import models

from .validators import validar_cpf


class Procedimento(models.Model):
    """Caso de apuração. Estados e transições seguem o ADR 0001."""

    class Estado(models.TextChoices):
        RASCUNHO = "rascunho", "Rascunho"
        EM_APURACAO = "em_apuracao", "Em apuração"
        ENCERRADO = "encerrado", "Encerrado"

    TRANSICOES = {
        Estado.RASCUNHO: {Estado.EM_APURACAO},
        Estado.EM_APURACAO: {Estado.ENCERRADO},
        Estado.ENCERRADO: set(),
    }

    titulo = models.CharField(max_length=255)
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.RASCUNHO,
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-criado_em"]

    def __str__(self):
        return f"{self.titulo} ({self.get_estado_display()})"

    def pode_transitar_para(self, novo_estado):
        return novo_estado in self.TRANSICOES[self.estado]

    def transitar_para(self, novo_estado):
        if not self.pode_transitar_para(novo_estado):
            raise ValidationError(
                f"Não é permitido ir de '{self.estado}' para '{novo_estado}'."
            )
        self.estado = novo_estado
        self.save(update_fields=["estado", "atualizado_em"])


class Parte(models.Model):
    """Pessoa que figura no procedimento. Só muda com o procedimento em rascunho."""

    class Papel(models.TextChoices):
        INVESTIGADO = "investigado", "Investigado"
        TESTEMUNHA = "testemunha", "Testemunha"
        DENUNCIANTE = "denunciante", "Denunciante"

    procedimento = models.ForeignKey(
        Procedimento,
        on_delete=models.PROTECT,
        related_name="partes",
    )
    nome = models.CharField(max_length=255)
    cpf = models.CharField(
        max_length=11,
        validators=[validar_cpf],
        help_text="Somente os 11 números.",
    )
    papel = models.CharField(max_length=20, choices=Papel.choices)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nome"]
        constraints = [
            models.UniqueConstraint(
                fields=["procedimento", "cpf"],
                name="parte_cpf_unico_por_procedimento",
            ),
        ]

    def __str__(self):
        return f"{self.nome} ({self.get_papel_display()})"

    def _exigir_rascunho(self):
        estado = (
            Procedimento.objects.filter(pk=self.procedimento_id)
            .values_list("estado", flat=True)
            .first()
        )
        if estado != Procedimento.Estado.RASCUNHO:
            raise ValidationError(
                "Partes só podem ser alteradas com o procedimento em rascunho."
            )

    def clean(self):
        if self.procedimento_id:
            self._exigir_rascunho()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self._exigir_rascunho()
        return super().delete(*args, **kwargs)
