Djask CLI
---------

This part of documentation will explain the usage of Djask CLI.

Introduction
============

Since Djask is based on Flask, its CLI utility inherits from Flask. Therefore,
the three basic commands - ``routes``, ``run`` and ``shell`` are nearly the 
same as those in Flask and you can skip the first section if you are familiar with Flask.

It won't be hard for you to migrate from Flask since Djask is fully compatible with Flask.
That is to say, your existing Flask projects and environment variables will still work with Djask.

Three commands inherited from Flask
===================================

This section just give a simple explanation of the three commands.

``djask routes`` will print out all the routes for your application.

``djask run`` will run your application. You can use the debugger with ``DJASK_ENV=development``
or call ``djask run`` with ``--debug``.

``djask shell`` will run an interactive shell with application context loaded, which means
the ``app`` object is available in the shell.

Creating a new app
==================

Djask CLI has a command ``djask createapp`` for you to quickly initialize a new app.

It receives an argument ``app_name`` which is the name of your app.

Here is an example, make sure you've installed Djask globally through ``pipx`` or something similar.

.. tabs::

   .. group-tab:: Mac OS X | Linux

      .. code-block:: text

         ~ $ djask createapp myapp
         ~ $ cd myapp
         ~/myapp $ ls
         myapp  requirements  tests  wsgi.py

   .. group-tab:: MS-Windows

      .. code-block:: text

         ~ >
         ~ > djask createapp myapp
         ~\myapp > ls
         myapp\
         requirements\
         tests\
         wsgi.py