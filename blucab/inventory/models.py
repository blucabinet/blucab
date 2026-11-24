from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from main.models import UserCabinet, Movie


class InventorySession(models.Model):
    """The current inventory run for one user."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="inventory_session",
        verbose_name=_("User"),
    )
    started_at = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Started at"),
    )
    current_batch_number = models.IntegerField(
        blank=True,
        null=True,
        default=1,
        verbose_name=_("Current batch number"),
    )

    default_viewed = models.BooleanField(
        blank=True,
        null=True,
        default=None,
        verbose_name=_("Default viewed"),
    )

    default_rented = models.BooleanField(
        blank=True,
        null=True,
        default=None,
        verbose_name=_("Default rented"),
    )

    default_cabinet = models.ForeignKey(
        UserCabinet,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        default=None,
        related_name="inventory_sessions",
        verbose_name=_("Default cabinet"),
    )

    class Meta:
        verbose_name = _("Inventory session")
        verbose_name_plural = _("Inventory sessions")

    def __str__(self):
        return f"{self.user.username}: {self.started_at}"


class InventoryScan(models.Model):
    """One unique EAN scanned during a user's current inventory run."""

    session = models.ForeignKey(
        InventorySession,
        on_delete=models.CASCADE,
        related_name="scans",
        verbose_name=_("Inventory session"),
    )
    ean = models.CharField(max_length=16, verbose_name=_("EAN/GTIN"))
    movie = models.ForeignKey(
        Movie,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="inventory_scans",
        verbose_name=_("Movie"),
    )
    scan_count = models.PositiveIntegerField(default=1, verbose_name=_("Scan count"))
    first_scanned_at = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("First scanned at"),
    )
    last_scanned_at = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Last scanned at"),
    )
    batch_number = models.IntegerField(
        blank=True,
        null=True,
        default=None,
        verbose_name=_("Batch number"),
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["session", "ean"],
                name="unique_inventory_session_ean",
            )
        ]
        ordering = ["first_scanned_at", "pk"]
        verbose_name = _("Inventory scan")
        verbose_name_plural = _("Inventory scans")

    def __str__(self):
        return f"{self.ean} ({self.scan_count})"
