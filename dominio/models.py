from django.core.exceptions import ValidationError
from django.db import models


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
