import re

from django.core.exceptions import ValidationError


def validar_cpf(valor):
    if not re.fullmatch(r"\d{11}", valor or ""):
        raise ValidationError("CPF deve ter 11 números, sem pontos nem traço.")
    if valor == valor[0] * 11:
        raise ValidationError("CPF inválido.")
    for posicao in (9, 10):
        soma = sum(int(valor[i]) * (posicao + 1 - i) for i in range(posicao))
        if (soma * 10) % 11 % 10 != int(valor[posicao]):
            raise ValidationError("CPF inválido.")
