from django.contrib import admin

from .models import Procedimento


@admin.register(Procedimento)
class ProcedimentoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "estado", "criado_em", "atualizado_em")
    list_filter = ("estado",)
    search_fields = ("titulo",)
    readonly_fields = ("criado_em", "atualizado_em")
