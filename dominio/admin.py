from django.contrib import admin

from .models import Parte, Procedimento


class ParteInline(admin.TabularInline):
    model = Parte
    extra = 0
    fields = ("nome", "cpf", "papel")

    def _em_rascunho(self, obj):
        return obj is None or obj.estado == Procedimento.Estado.RASCUNHO

    def has_add_permission(self, request, obj=None):
        return self._em_rascunho(obj) and super().has_add_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        return self._em_rascunho(obj) and super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return self._em_rascunho(obj) and super().has_delete_permission(request, obj)


@admin.register(Procedimento)
class ProcedimentoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "estado", "criado_em", "atualizado_em")
    list_filter = ("estado",)
    search_fields = ("titulo",)
    readonly_fields = ("estado", "criado_em", "atualizado_em")
    inlines = [ParteInline]
