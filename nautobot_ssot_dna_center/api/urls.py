"""Django API urlpatterns declaration for nautobot_ssot_dna_center plugin."""

from nautobot.apps.api import OrderedDefaultRouter

from nautobot_ssot_dna_center.api import views

router = OrderedDefaultRouter()
# add the name of your api endpoint, usually hyphenated model name in plural, e.g. "my-model-classes"
router.register("dnacinstance", views.DNACInstanceViewSet)


app_name = "nautobot_ssot_dna_center-api"
urlpatterns = router.urls
