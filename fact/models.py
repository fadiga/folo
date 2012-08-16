#!/usr/bin/env python
# encoding=utf-8
# maintainer: rgaudin

import datetime
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy, ugettext as _
import os, sys
import Image


class Owner(User):
    """ The web user who is also owner of the Organization
    """
    phone = models.CharField(max_length=30, blank=True,
                                verbose_name=("Telephone"))

    def __unicode__(self):
        return _(u'%(name)s') % {"name": self.username}


class Images(models.Model):
    """ Represents the organization's logo
    """
    name = models.ImageField(upload_to='org_images/', blank=True,\
                                    verbose_name=("image de la societe"))

    def __unicode__(self):
        return (u'%(image)s') % {'image': self.name}


class Organization(models.Model):
    """ Represents the company emmiting the invoices
    """
    name = models.CharField(max_length=150,\
                            verbose_name=("Nom de votre entreprise"))
    address = models.TextField(blank=True,\
                               verbose_name=("Adresse principale\
                                             de votre société"))
    address_extra = models.CharField(blank=True, max_length=20,\
                                    verbose_name=("Numero de téléphone\
                                                 de votre\
                                                entreprise"))
    address_extra2 = models.EmailField(blank=True,
                                     verbose_name=("Adresse électronique\
                                                    de votre entreprise"))
    legal_infos = models.TextField(blank=True,
                                    verbose_name=("Informations \
                                                   légales"))
    owner = models.ForeignKey(Owner, related_name='owner',\
                                     verbose_name=("Proprietaire"))
    image = models.ForeignKey(Images, verbose_name=("image de la societe"))

    def __unicode__(self):
        return _(u'%(name)s') % {"name": self.name}


class Client(models.Model):
    """ Represents the Client
    """
    name = models.CharField(max_length=150,
                            verbose_name=("Nom du client"),\
                            help_text=ugettext_lazy("Client Name"))
    address = models.TextField(blank=True,\
                               verbose_name=("Adresse du client"))
    organization = models.ForeignKey(Organization,\
                                     verbose_name=("Fournisseur"))

    def __unicode__(self):
        return _(u"%(name)s") % {'name': self.name}


class Invoice(models.Model):
    """ Represents an invoice
    """

    TYPE_FACT = 'f'
    TYPE_PROF = 'p'
    TYPES = (
        (TYPE_FACT, u"Facture"),
        (TYPE_PROF, u"Proforma")
    )
    location = models.CharField(max_length=50, blank=True,\
                                                verbose_name=("A"))
    client = models.ForeignKey(Client, verbose_name=("Doit"))
    type = models.CharField(max_length=30,
                            verbose_name=(""),\
                            choices=TYPES, default=TYPE_PROF)
    number = models.IntegerField(verbose_name=("Numero"))
    date = models.DateField(verbose_name=("Fait le"),\
                             default=datetime.datetime.today)
    subject = models.CharField(max_length=100, blank=True,\
                                              verbose_name=("Objet"))
    organization = models.ForeignKey(Organization,
                                     verbose_name=("Fournisseur"),\
                                     related_name='invoices')

    tax = models.BooleanField(default=False)
    tax_rate = models.PositiveIntegerField(blank=True, null=True,
                                            verbose_name=("Taux"),\
                                            default=18)

    @classmethod
    def get_next_number(cls, org):
        """
            Get a valid number automatically incremented from
            the higher one.
        """
        invoices = Invoice.objects.filter(organization=org)
        number = 1
        if invoices.count():
            last_invoice = invoices.latest('number')
            number += int(last_invoice.number)
        return number

    def __unicode__(self):
        return _(u"%(num)s - %(org)s : %(subject)s") % {
                                       'num': self.number,
                                       'org': self.organization,
                                       'subject': self.subject}


class InvoiceItem(models.Model):
    """ Represents an element of an invoice such as a product
    """
    invoice = models.ForeignKey(Invoice, blank=True, null=True)
    description = models.CharField(max_length=50,
                                   verbose_name=("Description"))
    quantity = models.PositiveIntegerField(verbose_name=("Quantite"))
    price = models.PositiveIntegerField(verbose_name=("Prix"))

    def __unicode__(self):
        return _(u"%(desc)s %(qty)s %(price)s") % {'qty': self.quantity,\
                                          'desc': self.description,
                                          'price': self.price}
