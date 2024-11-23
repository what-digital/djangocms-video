from cms.plugin_base import CMSPluginBase
from parler.admin import TranslatableAdmin
from cms.models import CMSPlugin
from parler.models import TranslatableModel


class TranslatablePlugin(TranslatableAdmin, CMSPluginBase):
    def response_add(self, request, obj, post_url_continue=None):
        """
        Overriding this because of conflicts between Parler and CMSPluginBase.
        """
        # Make sure ?language=... is included in the redirects.
        redirect = CMSPluginBase.response_add(self, request, obj, post_url_continue=post_url_continue)
        return self._patch_redirect(request, obj, redirect)

    def get_object(self, request, object_id, *args, **kwargs):
        """
        Overriding this because of conflicts between Parler and CMSPluginBase.
        """
        obj = self.model.objects.filter(pk=object_id).first()
        if obj is not None and self._has_translatable_model():  # Allow fallback to regular models.
            obj.set_current_language(self._language(request, obj), initialize=True)
        return obj


class TranslatablePluginModel(TranslatableModel):
    """
    Base class for translatable plugins.
    """
    class Meta:
        abstract = True

    def copy_relations(self, old_instance):
        if self.pk:
            for translation in old_instance.translations.all():
                translation.pk = None
                translation.master = self
                translation.save()

    def has_translation_or_fallback(self):
        if self.has_translation():
            return True
        for language in self.get_fallback_languages():
            if self.has_translation(language_code=language):
                return True
        return False
