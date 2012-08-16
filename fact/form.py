#!/usr/bin/env python
# -*- coding= UTF-8 -*-

import datetime

from models import *
from django import forms

from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.auth.models import User, Group


class ImagesForm(forms.ModelForm):

    file_ = forms.Field(widget=forms.FileInput, required=False)

    class Meta:
        model = Images


class ClientForm(forms.ModelForm):

    class Meta:
        model = Client
        exclude = ['organization']

    def __init__(self, request, *args, **kwargs):
        forms.ModelForm.__init__(self, *args, **kwargs)
        self.org = Organization.objects.get(owner__pk=request.user.pk)

    def save(self, *args, **kwargs):
        self.instance.organization = self.org
        return forms.ModelForm.save(self, *args, **kwargs)


class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, label=_("Username"))
    password = forms.CharField(max_length=100, label=_("Password"),\
                               widget=forms.PasswordInput)


class ModifInvoiceForm(forms.ModelForm):

    DATE_FORMAT = '%d/%m/%Y'

    class Meta:
        model = Invoice
        exclude = ['organization', 'type']


class HeaderForm(forms.ModelForm):

    DATE_FORMAT = '%d/%m/%Y'

    class Meta:
        model = Invoice
        exclude = ['organization', 'type']


class InvoiceForm(forms.ModelForm):

    DATE_FORMAT = '%d/%m/%Y'

    class Meta:
        model = Invoice
        exclude = ['organization', 'type']

    def __init__(self, request, *args, **kwargs):

        self.org = Organization.objects.get(owner__pk=request.user.pk)
        if request.POST:
            self.type_id = request.POST['type']

        # Affiche location par defaut
        lis, maxi = [], 0
        plus_utiliser = "Bamako"
        # On recupère les locaton d'un utilisateur et
        #on les mets dans une liste.
        if Invoice:
            for invoice in Invoice.objects.\
                                   filter(organization__owner=request.\
                                          user):
                lis.append(invoice.location)

            # On cherche la location la plus utiliser
            #pour être affiché par defaut
            for location in lis:
                if maxi < lis.count(location):
                    maxi = lis.count(location)
                    plus_utiliser = location

        # Afficher le numero auto
        # On cherche toutes les facture d'une orgnisation

        kwargs.setdefault('initial',
                         {'number': Invoice.get_next_number(self.org),\
                          'location': plus_utiliser})

        forms.ModelForm.__init__(self, *args, **kwargs)
        clients = Client.objects.filter(organization__name=self.org)
        self.fields['client'].queryset = clients
        self.fields['date'].widget.format = '%d/%m/%Y'
        self.fields['date'].widget.format = InvoiceForm.DATE_FORMAT
        self.fields['date'].input_formats = (InvoiceForm.DATE_FORMAT, )

    def save(self, *args, **kwargs):
        self.instance.organization = self.org

        if self.type_id == '1':
            self.instance.type = 'Facture'
        else:
            self.instance.type = 'Proforma'

        if not self.instance.tax_rate:
            self.instance.tax_rate = 1

        return forms.ModelForm.save(self, *args, **kwargs)


class AddOrganization(forms.ModelForm):

    class Meta:
        model = Organization


class InvoiceItemform(forms.ModelForm):

    class Meta:
        model = InvoiceItem


class Owner_editForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(Owner_editForm, self).__init__(*args, **kwargs)

    username = forms.CharField(max_length=100,\
                               label=("Nom d’utilisateur"))
    password = forms.CharField(max_length=100,\
                               label=("Mot de passe"),\
                               widget=forms.PasswordInput)
    password_confirmation = forms.CharField(max_length=100,\
                                           label=("Retapez le \
                                           mot de passe"),\
                                           widget=forms.PasswordInput)
    first_name = forms.CharField(max_length=100, label=("Nom"))
    last_name = forms.CharField(max_length=100, label=("Prénom"))
    email = forms.EmailField(label=("Email"), required=False)
    actif = forms.BooleanField(label=("Actif"), initial=True)


class AddOwner(forms.Form):

    def __init__(self, request, *args, **kwargs):
        super(AddOwner, self).__init__(*args, **kwargs)

    username = forms.CharField(max_length=100,\
                               label=("Nom d’utilisateur"))
    password = forms.CharField(max_length=100,\
                               label=("Mot de passe"),\
                               widget=forms.PasswordInput)
    password_confirmation = forms.CharField(max_length=100,\
                                            label=("Retapez le mot de \
                                                   passe"),\
                                            widget=forms.PasswordInput)
    first_name = forms.CharField(max_length=100, label=("Nom"))
    last_name = forms.CharField(max_length=100, label=("Prénom"))
    email = forms.EmailField(label=("Email"), required=False)
