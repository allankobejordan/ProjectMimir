from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import Procedimento


class ProcedimentoEstadoTests(TestCase):
    def setUp(self):
        self.procedimento = Procedimento.objects.create(titulo="Caso de teste")

    def test_nasce_em_rascunho(self):
        self.assertEqual(self.procedimento.estado, Procedimento.Estado.RASCUNHO)

    def test_rascunho_para_em_apuracao(self):
        self.procedimento.transitar_para(Procedimento.Estado.EM_APURACAO)
        self.procedimento.refresh_from_db()
        self.assertEqual(self.procedimento.estado, Procedimento.Estado.EM_APURACAO)

    def test_em_apuracao_para_encerrado(self):
        self.procedimento.transitar_para(Procedimento.Estado.EM_APURACAO)
        self.procedimento.transitar_para(Procedimento.Estado.ENCERRADO)
        self.procedimento.refresh_from_db()
        self.assertEqual(self.procedimento.estado, Procedimento.Estado.ENCERRADO)

    def test_encerrado_nao_volta(self):
        self.procedimento.transitar_para(Procedimento.Estado.EM_APURACAO)
        self.procedimento.transitar_para(Procedimento.Estado.ENCERRADO)
        with self.assertRaises(ValidationError):
            self.procedimento.transitar_para(Procedimento.Estado.EM_APURACAO)

    def test_rascunho_nao_pula_para_encerrado(self):
        with self.assertRaises(ValidationError):
            self.procedimento.transitar_para(Procedimento.Estado.ENCERRADO)
