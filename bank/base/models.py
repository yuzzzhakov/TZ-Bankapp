from django.db import models
from django.utils import timezone
from datetime import date, timedelta
from django.core.exceptions import ValidationError
import random
from .utils import CURRENCIES


class User(models.Model):
    name = models.CharField(max_length=15)
    surname = models.CharField(max_length=15)
    phone_number = models.CharField(max_length=12)

    def __str__(self):
        return f'[{self.id}] {self.name} - User'


class Account(models.Model):
    owner_info = models.CharField(max_length=30)
    number = models.CharField(max_length=16, unique=True, editable=False)
    balance = models.FloatField()
    currency = models.CharField(choices=CURRENCIES, max_length=3)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        if self.user:
            return f'[{self.id}] { self.user.name } - { self.balance } { self.currency } - Account'
        else:
            return f'[{self.id}] {self.owner_info} - { self.balance } { self.currency } - Account'

    def save(self, *args, **kwargs):
        if self.pk:
            super().save(*args, **kwargs)
        else:
            number = str(random.randint(0, 10000000))
            nulls = 8 - len(number)
            number = "0" * nulls + number
            self.number = '45001200' + number
            super().save(*args, **kwargs)


class BankCard(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    number = models.CharField(max_length=16, unique=True, editable=False)
    end_date = models.DateField(default=date.today() + timedelta(days=365))

    def __str__(self):
        return f'[{self.id}] {self.number} - BankCard'

    def save(self, *args, **kwargs):
        if self.pk:
            super().save(*args, **kwargs)
        else:
            number = str(random.randint(0, 10000000))
            nulls = 8 - len(number)
            number = "0" * nulls + number
            self.number = '45001200' + number
            super().save(*args, **kwargs)


class Transaction(models.Model):
    sum = models.FloatField()
    currency = models.CharField(choices=CURRENCIES, max_length=3)
    date_time = models.DateTimeField(default=timezone.now)
    STATUSES = [
        ('OK', 'OK'),
        ('CANCELED', 'CANCELED'),
        ('ERROR', 'ERROR'),
        ('IN PROCESS', 'IN PROCESS'),
    ]
    status = models.CharField(choices=STATUSES, max_length=10)

    def __str__(self):
        return f'[{self.id}] {self.sum} {self.currency}'


class InnerTransaction(models.Model):
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE)
    trans_from = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='trans_from')
    trans_to = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='trans_to')

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValidationError('you may not edit an existing %s' % self._meta.model_name)
        else:
            super().save(*args, **kwargs)
            self.trans_from.balance -= self.transaction.sum
            self.trans_from.save()
            self.trans_to.balance += self.transaction.sum
            self.trans_to.save()
            self.transaction.status = 'OK'
            self.transaction.date_time = timezone.now()
            self.transaction.save()


class ToOuterTransaction(models.Model):
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE)
    trans_from = models.ForeignKey(Account, on_delete=models.CASCADE)
    trans_to = models.CharField(max_length=26)

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValidationError('you may not edit an existing %s' % self._meta.model_name)
        else:
            super().save(*args, **kwargs)
            self.trans_from.balance -= self.transaction.sum
            self.trans_from.save()
            self.transaction.status = 'OK'
            self.transaction.date_time = timezone.now()
            self.transaction.save()


class FromOuterTransaction(models.Model):
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE)
    trans_from = models.CharField(max_length=26)
    trans_to = models.ForeignKey(Account, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValidationError('you may not edit an existing %s' % self._meta.model_name)
        else:
            super().save(*args, **kwargs)
            self.trans_to.balance += self.transaction.sum
            self.trans_to.save()
            self.transaction.status = 'OK'
            self.transaction.date_time = timezone.now()
            self.transaction.save()
