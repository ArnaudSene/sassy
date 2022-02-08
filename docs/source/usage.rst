
Usage
=====

.. _installation:

Installation
------------

To use sassy, first install it using pip:

.. code-block:: console

    $ pip install sassy

Create a project
----------------

To create a new project, provide a `project name`:

.. code-block:: console

    $ sassy new_project --create

.. note:: A git repository will be created.


Add a feature to your project
-----------------------------

To add a feature to your project.

.. code-block:: console

    $ sassy new_project new_feature --create


To add a feature by selecting folders in your project.

Options are:

- *a `applications`
- *d `domains`
- *i `interfaces`
- *p `providers`

.. epigraph:: Example: Create a feature `new_feature` in `applications` and `domains` folders.

.. code-block:: console

    $ sassy new_project new_feature *a,*d --create

Delete a feature in your project
--------------------------------

To delete a feature in your project.

.. code-block:: console

    $ sassy new_project new_feature --delete


To delete a feature by selecting folders in your project.

Options are:

- *a `applications`
- *d `domains`
- *i `interfaces`
- *p `providers`

.. epigraph:: Example: Delete a feature `new_feature` in `applications` and `domains` folders.


.. code-block:: console

    $ sassy new_project new_feature *a,*d --delete
