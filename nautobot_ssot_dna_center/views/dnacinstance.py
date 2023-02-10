"""Views for DNACInstance."""

from nautobot.core.views import generic

from nautobot_ssot_dna_center import filters, forms, models, tables


class DNACInstanceListView(generic.ObjectListView):
    """List view."""

    queryset = models.DNACInstance.objects.all()
    # These aren't needed for simple models, but we can always add
    # this search functionality.
    filterset = filters.DNACInstanceFilterSet
    filterset_form = forms.DNACInstanceFilterForm
    table = tables.DNACInstanceTable

    # Option for modifying the top right buttons on the list view:
    action_buttons = ("add", "export")


class DNACInstanceView(generic.ObjectView):
    """Detail view."""

    queryset = models.DNACInstance.objects.all()


class DNACInstanceCreateView(generic.ObjectEditView):
    """Create view."""

    model = models.DNACInstance
    queryset = models.DNACInstance.objects.all()
    model_form = forms.DNACInstanceForm


class DNACInstanceDeleteView(generic.ObjectDeleteView):
    """Delete view."""

    model = models.DNACInstance
    queryset = models.DNACInstance.objects.all()


class DNACInstanceEditView(generic.ObjectEditView):
    """Edit view."""

    model = models.DNACInstance
    queryset = models.DNACInstance.objects.all()
    model_form = forms.DNACInstanceForm


class DNACInstanceBulkImportView(generic.BulkImportView):
    """View for importing one or more DNACInstance records."""

    model = models.DNACInstance
    queryset = models.DNACInstance.objects.all()
    model_form = forms.DNACInstanceCSVImportForm


class DNACInstanceBulkDeleteView(generic.BulkDeleteView):
    """View for deleting one or more DNACInstance records."""

    queryset = models.DNACInstance.objects.all()
    table = tables.DNACInstanceTable


class DNACInstanceBulkEditView(generic.BulkEditView):
    """View for editing one or more DNACInstance records."""

    queryset = models.DNACInstance.objects.all()
    table = tables.DNACInstanceTable
    form = forms.DNACInstanceBulkEditForm
