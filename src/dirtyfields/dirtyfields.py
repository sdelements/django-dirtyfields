# Adapted from http://stackoverflow.com/questions/110803/dirty-fields-in-django
from django.db.models import ForeignKey
from django.db.models.fields.related import ReverseSingleRelatedObjectDescriptor

from django.db.models.signals import post_save



class DirtyFieldsMixin(object):
    def __init__(self, *args, **kwargs):
        super(DirtyFieldsMixin, self).__init__(*args, **kwargs)
        post_save.connect(
            reset_state, sender=self.__class__,
            dispatch_uid='{name}-DirtyFieldsMixin-sweeper'.format(
                name=self.__class__.__name__))
        reset_state(sender=self.__class__, instance=self)

    def get_field_value(self, field, **kwargs):
        value = None
        if isinstance(field, ForeignKey):
            if 'check_relationship' in kwargs and kwargs['check_relationship']:
                # If there is a ForeignKey that is not mandatory and without value,
                # we don't want to get this data and trigger a non-explicit "RelatedObjectDoesNotExist" error
                try:
                    value = getattr(self, field.name)
                except:
                    pass
        else:
            value = getattr(self, field.name)
        return value

    def _as_dict(self, check_relationship):
        all_field = {}
        kwargs = {'check_relationship': check_relationship}

        for field in self._meta.local_fields:
            value = self.get_field_value(field, **kwargs)
            if value is not None:
                all_field[field.name] = value

        return all_field

    def get_dirty_fields(self, check_relationship=False):
        # check_relationship indicates whether we want to check for foreign keys
        # and one-to-one fields or ignore them
        new_state = self._as_dict(check_relationship)
        all_modify_field = {}

        for key, value in new_state.iteritems():
            original_value = self._original_state[key]
            if value != original_value:
                all_modify_field[key] = original_value

        return all_modify_field

    def is_dirty(self, check_relationship=False):
        # in order to be dirty we need to have been saved at least once, so we
        # check for a primary key and we need our dirty fields to not be empty
        if not self.pk:
            return True
        return {} != self.get_dirty_fields(check_relationship=check_relationship)


def reset_state(sender, instance, **kwargs):
    # original state should hold all possible dirty fields to avoid
    # getting a `KeyError` when checking if a field is dirty or not
    instance._original_state = instance._as_dict(check_relationship=True)
