# Application templates

To jumpstart developing new Conway-based applications, Conway provides a number of *application templates*.

These can be used to create a new project for a new Conway-based application. The resulting project structure would
contain:

* All required repos, as per Conway patterns

* Sample implementation of the main Conway domain objects, tests, and operational tooling for that new application

# Implementation note

This functionality is based on ``Jinja2`` template functionality, but unlike ``Jinja2``, templating is limited to the
contents of files. It is also supported to the names of folders, and so the generated code will not necessarily lie
in the exact same relative paths as the templates from which the code is generated, since those relative paths are templated
in the case of templates.

For example, a template like ``params.app_code.svc/src/params.app_module/application/params.app_module._application.py`` might
result in the generation of a file called ``cash.svc/src/cash_management/application/cash_management_application.py``.

Template variables are always prefixed with the ``params.`` prefix, for ease of identification, both in the content of
template files and in the paths of those template files.

# Supported templates

Different templates are provided to allow the operator to select the one that is a best fit.

All templates are identified by a numberical identifier, and at present the following templates are supported:

* 101: this is a "basic", "minimalist" template. It presuposes only the existence of business logic (the services) available
        as a library, with all invocation of the services done by Jupyter Notebooks. This is "minimalist" because it
        does not include scaffolding for other means of accessing the services. For example, it provides not scaffolding
        for a web server providing REST APIs for the services, or a UI for a human to trigger services, nor a CLI for 
        shell-based service invocation.