ContactsApp documentation
=========================


.. toctree::
   :maxdepth: 3
   :caption: Contents:


REST API main
===================================
Main file

app_main.\ **lifespan**\ (app: FastAPI)

    Define the lifespan of the FastAPI application.

    This function manages the lifecycle of the FastAPI application, initializing and closing
    resources such as Redis and FastAPILimiter during the app's lifespan.

    Args:
        app (FastAPI): The FastAPI application instance.

    Yields:
        Allows the FastAPI application to run within this context, managing resources.

app_main.\ **root**\ () -> dict

    Health check endpoint to verify that the server is running.

    This endpoint can be used to confirm that the server is alive and
    responding to requests. It returns a simple message indicating the server
    status.

    Returns:
        dict: A dictionary containing a message indicating that
            the server is alive.

REST API database
===================================
.. automodule:: src.database
  :members:
  :undoc-members:
  :show-inheritance:


Contacts Router
===================================
.. automodule:: src.contacts.router
  :members:
  :undoc-members:
  :show-inheritance:


Contacts Models
===================================
.. automodule:: src.contacts.models
  :members:
  :undoc-members:
  :show-inheritance:


Contacts Schemas
===================================
.. automodule:: src.contacts.schemas
  :members:
  :undoc-members:
  :show-inheritance:


Contacts CRUD operations
===================================
.. automodule:: src.contacts.crud
  :members:
  :undoc-members:
  :show-inheritance:


Authentication Router
===================================
.. automodule:: src.auth.router
  :members:
  :undoc-members:
  :show-inheritance:


Authentication Models
===================================
.. automodule:: src.auth.models
  :members:
  :undoc-members:
  :show-inheritance:


Authentication Schemas
===================================
.. automodule:: src.auth.schemas
  :members:
  :undoc-members:
  :show-inheritance:


Authentication module
===================================
.. automodule:: src.auth.auth
  :members:
  :undoc-members:
  :show-inheritance:


Authentication CRUD ops
===================================
.. automodule:: src.auth.crud
  :members:
  :undoc-members:
  :show-inheritance:


Authentication Email
===================================
.. automodule:: src.auth.mail
  :members:
  :undoc-members:
  :show-inheritance:


Indices and tables
===================================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
