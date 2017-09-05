############
Contributing
############

This document provides guidelines for people who want to contribute to the
`django-docusign` project.


**************
Create tickets
**************

Please use `django-docusign bugtracker`_ **before** starting some work:

* check if the bug or feature request has already been filed. It may have been
  answered too!

* else create a new ticket.

* if you plan to contribute, tell us, so that we are given an opportunity to
  give feedback as soon as possible.

* Then, in your commit messages, reference the ticket with some
  ``refs #TICKET-ID`` syntax.


******************
Use topic branches
******************

* Work in branches.

* Prefix your branch with the ticket ID corresponding to the issue. As an
  example, if you are working on ticket #23 which is about contribute
  documentation, name your branch like ``23-contribute-doc``.

* If you work in a development branch and want to refresh it with changes from
  master, please `rebase`_ or `merge-based rebase`_, i.e. do not merge master.


***********
Fork, clone
***********

Clone `django-docusign` repository (adapt to use your own fork):

.. code:: sh

   git clone git@github.com:novapost/django-docusign.git
   cd django-docusign/


*************
Usual actions
*************

The `Makefile` is the reference card for usual actions in development
environment:

* Install development toolkit with `pip`_: ``make develop``.

* Run tests with `tox`_: ``make test``.

* Build documentation: ``make documentation``. It builds `Sphinx`_
  documentation in `var/docs/html/index.html`.

* Release `django-docusign` project with `zest.releaser`_: ``make release``.

* Cleanup local repository: ``make clean``, ``make distclean`` and
  ``make maintainer-clean``.

See also ``make help``.


****************************************
Use private credentials to run the tests
****************************************

The test suite contains several integration tests, so it requires valid
DocuSign account credentials. The test suite reads environment variables to
get the setup. Here is an example to run the tests:

.. code:: sh

   DOCUSIGN_ROOT_URL='https://demo.docusign.net/restapi/v2' \
   DOCUSIGN_USERNAME='your-username' \
   DOCUSIGN_PASSWORD='your-password' \
   DOCUSIGN_INTEGRATOR_KEY='your-integrator-key' \
   DOCUSIGN_TEST_TEMPLATE_ID='UUID-of-your-docusign-template' \
   DOCUSIGN_TEST_SIGNER_RETURN_URL='http://example.com/signer-return/' \
   make test


.. rubric:: Notes & references

.. target-notes::

.. _`django-docusign bugtracker`: https://github.com/novafloss/django-docusign/issues
.. _`rebase`: http://git-scm.com/book/en/Git-Branching-Rebasing
.. _`merge-based rebase`: http://tech.novapost.fr/psycho-rebasing-en.html
.. _`pip`: https://pypi.python.org/pypi/pip/
.. _`tox`: https://pypi.python.org/pypi/tox/
.. _`Sphinx`: https://pypi.python.org/pypi/Sphinx/
.. _`zest.releaser`: https://pypi.python.org/pypi/zest.releaser/
