API
===

.. module:: djask

Application Object
------------------

.. autoclass:: Djask
   :members: model, register_model, register_models

Blueprint Objects
-----------------

.. autoclass:: Blueprint
   :members: model, register_model, register_models

.. autoclass:: APIBlueprint
   :members: model, register_model, register_models

Admin Functionalities
---------------------

.. autoclass:: djask.admin.ext.Admin
   :members:

.. autofunction:: djask.admin.decorators.admin_required

More Information
--------------------

This documentation only gives new functionalities and differences between those implemented in Djask
and those in Flask and APIFlask.

To learn more about :py:meth:`Djask`, please refer to the documentations of Flask and APIFlask:

- `Flask Documentation <https://flask.palletsprojects.com/>`_
- `APIFlask Documentation <https://apiflask.com/>`_
