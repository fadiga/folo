from django.conf.urls.defaults import *
import settings
from settings import MEDIA_ROOT, DEBUG
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # (r'^facture/', include('facture.foo.urls')),
    url(r"^add_owner/$", "fact.views.add_owner", name="add_owner"),
    url(r"^add_client/$", "fact.views.add_client", name="add_client"),
    url(r"^owner/$", "fact.views.owner", name="owner"),
    url(r"^owner_edit/(?P<id>\d+)$", "fact.views.owner_edit",\
                                    name="owner_edit"),
    url(r"^dashboard/(?P<num>\d+)*$", "fact.views.dashboard",\
                                    name="dashboard"),
    url(r"^duplicate/(?P<id>\d+)$", "fact.views.duplicate",\
                                    name="duplicate"),
    url(r"^modification/(?P<num>\d+)$", "fact.views.modification",\
                                        name="modification"),
    url(r"^delete/(?P<id>\d+)$", "fact.views.delete", name="delete"),
    url(r"^add_invoice/$", "fact.views.add_invoice", name="add_invoice"),
    url(r"^add_organization/(?P<id>\d+)?$", "fact.views.add_organization",\
                                        name="add_organization"),
    url(r"^edit_organization/(?P<id>\d+)?$", "fact.views.edit_organization",\
                                        name="edit_organization"),
    url(r"^delete_confirm/(?P<id>\d+)$", "fact.views.delete_confirm",\
                                        name="delete_confirm"),
    url(r"^$", "fact.views.login", name="login"),

    url(r"^edit_organization/logo(?P<num>\d+)*$",\
                                    "fact.views.choose_logo_editorg",\
                                            name="choose_logo_editorg"),

    url(r"^add_organization/logo/(?P<num>\d+)*$",\
                                "fact.views.choose_logo_addorg",\
                                        name="choose_logo_addorg"),

    url(r"^logout/$", 'fact.views.logout', name='logout'),

    url(r"^invoice_done/$", "fact.views.invoice_done",\
                                    name="invoice_done"),

    url(r"^show_invoice/(?P<id>\d+)$", "fact.views.show_invoice",\
                                            name="show_invoice"),

    url(r"^add_invoice/(?P<num>\d+)$", "fact.views.add_invoice", \
                                                name="add_item"),

    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),

    # Pour la gerenation du PDF
    url(r"^PDF/(?P<id>\d+)$", "fact.views.PDF_view",\
                                name="PDF_invoice_done"),

    url(r'^static/(?P<path>.*)$',
             'django.views.static.serve',
             {'document_root': MEDIA_ROOT, 'show_indexes': True}),

)
handler404 = "folo.fact.views.my_custom_404_view"
