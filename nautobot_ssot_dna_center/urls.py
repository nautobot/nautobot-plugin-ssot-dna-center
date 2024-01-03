"""Django urlpatterns declaration for nautobot_ssot_dna_center plugin."""
from django.urls import path
from nautobot.extras.views import ObjectChangeLogView

from nautobot_ssot_dna_center import models
from nautobot_ssot_dna_center.views import dnacinstance

urlpatterns = [
    # DNACInstance URLs
    path("dnacinstance/", dnacinstance.DNACInstanceListView.as_view(), name="dnacinstance_list"),
    # Order is important for these URLs to work (add/delete/edit) to be before any that require uuid/slug
    path("dnacinstance/add/", dnacinstance.DNACInstanceCreateView.as_view(), name="dnacinstance_add"),
    path("dnacinstance/delete/", dnacinstance.DNACInstanceBulkDeleteView.as_view(), name="dnacinstance_bulk_delete"),
    path("dnacinstance/edit/", dnacinstance.DNACInstanceBulkEditView.as_view(), name="dnacinstance_bulk_edit"),
    path("dnacinstance/import/", dnacinstance.DNACInstanceBulkImportView.as_view(), name="dnacinstance_import"),
    path("dnacinstance/<uuid:uuid>/", dnacinstance.DNACInstanceView.as_view(), name="dnacinstance"),
    path("dnacinstance/<uuid:uuid>/delete/", dnacinstance.DNACInstanceDeleteView.as_view(), name="dnacinstance_delete"),
    path("dnacinstance/<uuid:uuid>/edit/", dnacinstance.DNACInstanceEditView.as_view(), name="dnacinstance_edit"),
    path(
        "dnacinstance/<uuid:uuid>/changelog/",
        ObjectChangeLogView.as_view(),
        name="dnacinstance_changelog",
        kwargs={"model": models.DNACInstance},
    ),
]
