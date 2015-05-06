from django.db.models.signals import post_save
from django.core.exceptions import ObjectDoesNotExist


class DirtyFieldsMixin(object):
    """
    Model mixin to track dirty fields.

    This mixin adds dirty field tracking functionality to the model. It
    provides methods to query if the instance has changed, or if a particular
    field has changed, and to get back the original values of the field.
    """

    def __init__(self, *args, **kwargs):
        super(DirtyFieldsMixin, self).__init__(*args, **kwargs)

        # reset the state whenever an instance is saved
        dispatch_uid = "{0}-DirtyFieldsSweeper".format(self.__class__.__name__)
        post_save.connect(self._reset_state, sender=self.__class__, dispatch_uid=dispatch_uid)

        self._reset_state(sender=self.__class__, instance=self)

    def _reset_state(self, **kwargs):
        """Reset the original state to the current state."""
        self._original_state = self._as_dict(check_relationship=True)

    def _as_dict(self, check_relationship=False):
        """Serialize the fields to a dictionary."""
        fields = {}

        for field in self._meta.local_fields:
            if field.rel and not check_relationship:
                continue
            try:
                # for relational field, we just want the id to avoid extra queries.
                attr = field.name if not field.rel else "{0}_id".format(field.name)
                fields[field.name] = getattr(self, attr)
            except ObjectDoesNotExist:
                pass

        return fields

    def get_dirty_fields(self, check_relationship=False):
        """Return the fields that have changed along with their original values."""
        new_state = self._as_dict(check_relationship)

        modified_fields = {}
        for field_name, value in new_state.items():
            original_value = self._original_state[field_name]
            if value != original_value:
                modified_fields[field_name] = original_value

        return modified_fields

    def is_dirty(self, check_relationship=False):
        """Return whether the instance has changed."""
        # instance needs to be saved in order to be dirty
        if not self.pk:
            return True

        # check if any fields are dirty
        return bool(self.get_dirty_fields(check_relationship=check_relationship))

    def is_field_dirty(self, field_name, check_relationship=False):
        """Return whether a particular field has changed."""
        if field_name not in self._as_dict(check_relationship).keys():
            raise ValueError("Invalid field name")

        return field_name in self.get_dirty_fields(check_relationship)

    def original_field_value(self, field_name):
        """Return the original field value."""
        if field_name not in self._as_dict(True).keys():
            raise ValueError("Invalid field name")

        return self._original_state[field_name]