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

Admin Decorators
----------------

.. autoclass:: djask.admin.ext.Admin
   :members:

.. autofunction:: djask.admin.decorators.admin_required

.. autofunction:: djask.admin.api.decorators.admin_required_api

Helper Functions
----------------

.. automodule:: djask.helpers
   :members:

Models
------

.. automodule:: djask.auth.models
   :members:

.. automodule:: djask.auth.abstract
   :members:

.. automodule:: djask.auth.anonymous
   :members:

.. autoclass:: djask.db.models.Model
   :members: to_dict, to_schema

   .. autoattribute:: id
   .. autoattribute:: created_at
   .. autoattribute:: updated_at


More Information
----------------

This documentation only gives new functionalities and differences between those implemented in Djask
and those in Flask and APIFlask.

To learn more about Djask, please refer to the documentations of Flask and APIFlask:

- `Flask Documentation <https://flask.palletsprojects.com/>`_
- `APIFlask Documentation <https://apiflask.com/>`_
