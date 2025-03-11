from django.db import models

class Role(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    permissions = models.JSONField()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'role'
