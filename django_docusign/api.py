"""Declaration of API shortcuts.

Everything declared (or imported) in this module is exposed in
:mod:`django_docusign.api` package, i.e. available when one does
``from django_docusign import api as django_docusign``.

Here are the motivations of such an "api" module:

* as a `django-docusign` library user, in order to use `django-docusign`, I
  just do ``from django_docusign import api as django_docusign``.
  It is enough for most use cases. I do not need to bother with more
  `django_docusign` internals. I know this API will be maintained, documented,
  and not deprecated/refactored without notice.

* as a `django-docusign` library developer, in order to maintain
  `django-docusign` API, I focus on things declared in
  :mod:`django_docusign.api`. It is enough. It is required. I take care of this
  API. If there is a change in this API between consecutive releases, then I
  use :class:`DeprecationWarning` and I mention it in release notes.

It also means that things not exposed in :mod:`django_docusign.api` are not
part of the deprecation policy. They can be moved, changed, removed without
notice.

"""
from django_docusign.backend import DocuSignBackend
from django_docusign.forms import SignerForm
from django_docusign.views import SignerReturnView

__all__ = ['DocuSignBackend', 'SignerForm', 'SignerReturnView']
