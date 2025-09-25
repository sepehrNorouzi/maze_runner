import pickle

from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    updated_time = models.DateTimeField(verbose_name=_("Updated time"), auto_now=True)
    created_time = models.DateTimeField(verbose_name=_("Created time"), auto_now_add=True, )

    class Meta:
        abstract = True


class SingletonModel(BaseModel):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.__class__.objects.count() > 1:
            raise ValidationError(_(f"There can only be one {self.__class__.__name__}."))
        super(SingletonModel, self).save(*args, **kwargs)


class SingletonCachableModel(SingletonModel):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        super(SingletonCachableModel, self).save(*args, **kwargs)
        cache.set(self.get_cache_key(), pickle.dumps(self))

    @classmethod
    def get_cache_key(cls):
        return f'{cls.__name__.upper()}_CACHE_KEY'

    @classmethod
    def load(cls):
        cached = cache.get(cls.get_cache_key())
        if cached:
            obj = pickle.loads(cached)
        else:
            obj = cls.objects.first()
            if not obj:
                return cls.objects.create()
            cache.set(cls.get_cache_key(), pickle.dumps(obj))
        return obj


class CachableModel(BaseModel):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        super(CachableModel, self).save(*args, **kwargs)
        cache.set(self.get_cache_key(), pickle.dumps(self.__class__.objects.filter(is_active=True)))

    @classmethod
    def get_cache_key(cls):
        return f'{cls.__name__.upper()}_CACHE_KEY'

    @classmethod
    def load(cls):
        cached = cache.get(cls.get_cache_key())
        if cached:
            obj = pickle.loads(cached)

        else:
            obj = cls.objects.filter(is_active=True)
            cache.set(cls.get_cache_key(), pickle.dumps(obj))

        return obj


class Configuration(SingletonCachableModel):
    app_name = models.CharField(verbose_name=_("App Name"), max_length=255, default="maze_runner")
    app_version = models.CharField(verbose_name=_("App Version"), max_length=100, default='1.0.0')
    maintenance_mode = models.BooleanField(verbose_name=_('Maintenance mode'), default=False)

    class Meta:
        verbose_name = _("Configuration")
        verbose_name_plural = _("Configurations")

    def __str__(self):
        return f'{self.app_name}_{self.app_version}'

    @classmethod
    def load(cls):
        cached = cache.get(cls.get_cache_key())
        if cached:
            obj = pickle.loads(cached)

        else:
            obj, c = cls.objects.get_or_create(is_active=True)
            cache.set(cls.get_cache_key(), pickle.dumps(obj))

        return obj
