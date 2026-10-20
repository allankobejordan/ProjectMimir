from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, models, transaction
from django.test import TestCase
from django.urls import reverse

from .models import Parte, Procedimento
from .validators import validar_cpf

CPF_VALIDO = "52998224725"
OUTRO_CPF_VALIDO = "11144477735"


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


class ValidarCpfTests(TestCase):
    def test_aceita_cpf_valido(self):
        validar_cpf(CPF_VALIDO)

    def test_recusa_digito_verificador_errado(self):
        with self.assertRaises(ValidationError):
            validar_cpf("52998224724")

    def test_recusa_cpf_com_pontuacao(self):
        with self.assertRaises(ValidationError):
            validar_cpf("529.982.247-25")

    def test_recusa_digitos_repetidos(self):
        with self.assertRaises(ValidationError):
            validar_cpf("11111111111")


class ParteTests(TestCase):
    def setUp(self):
        self.procedimento = Procedimento.objects.create(titulo="Caso de teste")

    def _criar_parte(self, procedimento=None, cpf=CPF_VALIDO):
        return Parte.objects.create(
            procedimento=procedimento or self.procedimento,
            nome="Fulano",
            cpf=cpf,
            papel=Parte.Papel.TESTEMUNHA,
        )

    def test_cria_parte_em_rascunho(self):
        parte = self._criar_parte()
        self.assertEqual(self.procedimento.partes.get(), parte)

    def test_recusa_cpf_invalido(self):
        with self.assertRaises(ValidationError):
            self._criar_parte(cpf="12345678900")

    def test_recusa_mesmo_cpf_no_mesmo_procedimento(self):
        self._criar_parte()
        with self.assertRaises(ValidationError):
            self._criar_parte()

    def test_aceita_mesmo_cpf_em_outro_procedimento(self):
        outro = Procedimento.objects.create(titulo="Outro caso")
        self._criar_parte()
        self._criar_parte(procedimento=outro)
        self.assertEqual(Parte.objects.filter(cpf=CPF_VALIDO).count(), 2)

    def test_banco_recusa_duplicata_mesmo_sem_passar_pelo_model(self):
        self._criar_parte()
        duplicada = Parte(
            procedimento=self.procedimento,
            nome="Fulano",
            cpf=CPF_VALIDO,
            papel=Parte.Papel.TESTEMUNHA,
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            Parte.objects.bulk_create([duplicada])

    def test_recusa_nova_parte_fora_do_rascunho(self):
        self.procedimento.transitar_para(Procedimento.Estado.EM_APURACAO)
        with self.assertRaises(ValidationError):
            self._criar_parte()

    def test_recusa_alterar_parte_fora_do_rascunho(self):
        parte = self._criar_parte()
        self.procedimento.transitar_para(Procedimento.Estado.EM_APURACAO)
        parte.nome = "Outro nome"
        with self.assertRaises(ValidationError):
            parte.save()

    def test_recusa_apagar_parte_fora_do_rascunho(self):
        parte = self._criar_parte()
        self.procedimento.transitar_para(Procedimento.Estado.EM_APURACAO)
        with self.assertRaises(ValidationError):
            parte.delete()
        self.assertTrue(Parte.objects.filter(pk=parte.pk).exists())

    def test_procedimento_com_partes_nao_pode_ser_apagado(self):
        self._criar_parte()
        with self.assertRaises(models.ProtectedError):
            self.procedimento.delete()

    def test_duas_partes_com_cpfs_diferentes(self):
        self._criar_parte()
        self._criar_parte(cpf=OUTRO_CPF_VALIDO)
        self.assertEqual(self.procedimento.partes.count(), 2)


class ProcedimentoAdminTests(TestCase):
    def setUp(self):
        usuario = get_user_model().objects.create_superuser("admin", "admin@exemplo.com")
        self.client.force_login(usuario)
        self.procedimento = Procedimento.objects.create(titulo="Caso de teste")
        Parte.objects.create(
            procedimento=self.procedimento,
            nome="Fulano",
            cpf=CPF_VALIDO,
            papel=Parte.Papel.TESTEMUNHA,
        )
        self.url = reverse("admin:dominio_procedimento_change", args=[self.procedimento.pk])

    def test_estado_nao_e_editavel(self):
        resposta = self.client.get(self.url)
        self.assertNotContains(resposta, 'name="estado"')

    def test_partes_editaveis_em_rascunho(self):
        resposta = self.client.get(self.url)
        self.assertContains(resposta, 'name="partes-0-nome"')

    def test_partes_somente_leitura_fora_do_rascunho(self):
        self.procedimento.transitar_para(Procedimento.Estado.EM_APURACAO)
        resposta = self.client.get(self.url)
        self.assertContains(resposta, "Fulano")
        self.assertNotContains(resposta, 'name="partes-0-nome"')
