from django.urls import include, path

import contacts.views as contact_views

app_name = "contacts"

urlpatterns = [
    path(
        "confirmed_contact/",
        contact_views.ConfirmedContactView.as_view(),
        name="rest_confirmed_contact",
    ),
]
