from django.contrib.auth.models import User
from django.db import models
from simple_history.models import HistoricalRecords

from .fields import EncryptedCharField


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    telefone = models.CharField(max_length=20, blank=True)
    cpf = EncryptedCharField(blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfis"

    def __str__(self):
        return f"Perfil de {self.user.get_full_name() or self.user.username}"


class LoginHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="login_history")
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Histórico de Login"
        verbose_name_plural = "Histórico de Logins"
        ordering = ["-timestamp"]

    def __str__(self):
        status = "OK" if self.success else "FALHOU"
        return f"{self.user.username} [{status}] — {self.timestamp:%d/%m/%Y %H:%M}"
