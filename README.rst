Django Dirty Fields
===================

Makes a Mixing available that will give you the methods:

 * is\_dirty()
 * get\_dirty\_fields()
 * is\_field\_dirty(field\_name)
 * original\_field\_value(field\_name)


Using the Mixin in the Model
----------------------------

::
    
    from django.db import models
    from dirtyfields import DirtyFieldsMixin

    class TestModel(DirtyFieldsMixin, models.Model):
        """A simple test model to test dirty fields mixin with"""
        boolean = models.BooleanField(default=True)
        characters = models.CharField(blank=True, max_length=80)
    

Using it in the shell
---------------------

::

    (ve)$ ./manage.py shell
    >>> from testing_app.models import TestModel
    >>> tm = TestModel(boolean=True,characters="testing")
    >>> tm.save()
    >>> tm.is_dirty()
    False
    >>> tm.get_dirty_fields()
    {}
    >>> tm.boolean = False
    >>> tm.is_dirty()
    True
    >>> tm.get_dirty_fields()
    {'boolean': True}
    >>> tm.characters = "have changed"
    >>> tm.is_dirty()
    True
    >>> tm.get_dirty_fields()
    {'boolean': True, 'characters': 'testing'}
    >>> tm.is_field_dirty('characters')
    True
    >>> tm.original_field_value('characters')
    u'testing'
    >>> tm.save()
    >>> tm.is_dirty()
    False
    >>> tm.get_dirty_fields()
    {}
    >>> 


Checking foreign key fields.
----------------------------
By default, dirty functions are not checking foreign keys. If you want to also take these relationships into account, use ``check_relationship`` parameter:

::

    (ve)$ ./manage.py shell
    >>> from testing_app.models import TestModel
    >>> tm = TestModel(fkey=obj1)
    >>> tm.save()
    >>> tm.is_dirty()
    False
    >>> tm.get_dirty_fields()
    {}
    >>> tm.fkey = obj2
    >>> tm.is_dirty()
    False
    >>> tm.is_dirty(check_relationship=True)
    True
    >>> tm.get_dirty_fields()
    {}
    >>> tm.get_dirty_fields(check_relationship=True)
    {'fkey': obj1}


Why would you want this?
------------------------

When using signals_, especially pre_save_, it is useful to be able to see what fields have changed or not. A signal could change its behaviour depending on whether a specific field has changed, whereas otherwise, you only could work on the event that the model's `save()` method had been called.

Credits
-------

Forked from https://github.com/smn/django-dirtyfields
