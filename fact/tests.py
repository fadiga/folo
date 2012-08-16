#!/usr/bin/env python
# -*- coding= UTF-8 -*-
"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from cel import cel
from django.test.client import Client
from django.contrib.auth import (authenticate, login as django_login,
                                 logout as django_logout)


class ViewsTest(TestCase):

    def setUp(self):
        """
        on cré les utilisateurs dont on aura besoin
        """
        self.logged_admin = Client()
        self.logged_user = Client()
        self.anonymous_client = Client()
        from fact.models import Owner
        # Ici on s'identifie. ca permet de tester la vue login
        # mais aussi ca garde le cookie donc les autres vues seront comme
        # si on est loggé. Il faut le LOGIN_URL dans settings.
        logged_admin = self.logged_admin.login(username='admin',\
                                               password='admin')
        # on teste que l'on est bien loggé
        self.assertTrue(logged_admin)
        # on test la vue add_owner
        response = self.logged_admin.post('/add_owner/',
                                    {'username': 'Dolo',
                                    'password': 'alou',
                                    "password_confirmation": 'alou',
                                    'first_name': 'wise',
                                    'last_name': 'dolo',
                                    'email': 'lion@alzz.fr'})
        logged_user = self.logged_user.login(username='Dolo', password='alou')
        self.assertTrue(logged_user)
        self.own = Owner.objects.get(id=2)

    def test_add_owner(self):
        """
            test la vue ajout d'utilisateur
        """
        self.assertEqual(self.own.__unicode__(), "Dolo")
        self.assertEqual(self.own.username, 'Dolo')
        self.assertEqual(self.own.last_name, 'dolo')
        self.assertEqual(self.own.first_name, 'wise')

    def test_view_edit_owner(self):
        """
            test la vue ajout d'utilisateur
        """
        from fact.models import Owner

        #On test la vue owner_edit
        response = self.logged_admin.post('/owner_edit/2',
                                    {'username': 'ami',
                                    'password': 'mimi',
                                    "password_confirmation": 'mimi',
                                    'first_name': 'Aminata',
                                    'last_name': 'dolo',
                                    'email': 'lllal@alzz.fr',
                                    'actif': 'on'})
        own = Owner.objects.get(id=2)
        self.assertEqual(own.__unicode__(), "ami")
        self.assertEqual(own.email, 'lllal@alzz.fr')
        self.assertEqual(own.username, 'ami')
        self.assertEqual(own.password, 'mimi')
        self.assertEqual(own.last_name, 'dolo')
        self.assertEqual(own.first_name, 'Aminata')

        #On test la vue owner_edit sans etre identifier
        response1 = self.anonymous_client.post('/owner_edit/2',
                                    {'username': 'ami',
                                    'password': 'mimi',
                                    "password_confirmation": 'mimi',
                                    'first_name': 'Aminata',
                                    'last_name': 'dolo',
                                    'email': 'lllal@alzz.fr',
                                    'actif': 'on'})
        self.assertRedirects(response1,\
                             "http://testserver/?next=/owner_edit/2")

    def test_view_add_client(self):
        """
            test la vue ajout de client
        """
        from fact.models import Organization, Client

        # on créé une Organization car c'est necessaire dans la vue
        # add_client.
        # normalement, il faudrait le créer a partir d'un test sur la vue
        # qui créé les org.
        org = Organization.objects.create(name=u"Mimi couture ",\
                                          owner=self.own)

        # Ici on s'identifie. ca permet de tester la vue login
        # mais aussi ca garde le cookie donc les autres vues seront comme
        # si on est loggé. Il faut le LOGIN_URL dans settings.

        # on teste la vue add_client
        response = self.logged_user.post('/add_client/',\
                                        {'name': 'tief',\
                                         'address': 'Bamako'})
        client = Client.objects.get(id=1)
        self.assertEqual(client.__unicode__(), "tief")
        self.assertEqual(client.address, "Bamako")
        # On test la views ajout client sans etre identifier
        response1 = self.anonymous_client.post('/add_client/',\
                                                {'name': 'tief',\
                                                'address': 'Bamako'})
        self.assertRedirects(response1,\
                             "http://testserver/?next=/add_client/")

    def test_view_add_invoice(self):
        """
           test la vue ajout de facture
        """
        from fact.models import (Organization, Owner, Client,
                                 Invoice, InvoiceItem)

        org = Organization.objects.create(name="Alou-services",
                                          owner=self.own)
        client = Client.objects.create(name='tief',
                                       address='Bamako',
                                       organization=org)

        # On test la views ajout de facture
        response = self.logged_user.post('/add_invoice/',\
                                    {
                                    "client": client.id,
                                    "tax": "on", "number": "8",
                                    "date": "25/10/2010",
                                    "subject": "vente d'ordi",
                                    "location": "Bamako",
                                    "type": "Facture",
                                    "tax_rate": "18",

                                    "form-TOTAL_FORMS": "3",
                                    "form-INITIAL_FORMS": "0",
                                    "form-MAX_NUM_FORMS": "",

                                    "form-0-description": "oridinateur",
                                    "form-0-quantity": "80",
                                    "form-0-price": "1000",

                                    "form-1-description": "",
                                    "form-1-quantity": "",
                                    "form-1-price": "",

                                    "form-2-description": "",
                                    "form-2-quantity": "",
                                    "form-2-price": "",

                                    "add_invoice": "Enregistrer",
                                    })
        invoice = Invoice.objects.get(id=1)
        invoiceitem = InvoiceItem.objects.get(id=1)
        self.assertEqual(invoice.__unicode__(),
                         "8 - Alou-services : vente d'ordi")
        self.assertEqual(invoiceitem.__unicode__(),
                         "oridinateur 80 1000")

        # On test la views ajout de facture sans etre identifier
        response1 = self.anonymous_client.post('/add_invoice/', {
                                    "client": client.id,
                                    "tax": "on", "number": "8",
                                    "date": "25/10/2010",
                                    "subject": "vente d'ordi",
                                    "location": "Bamako",
                                    "type": "Facture",
                                    "tax_rate": "18",

                                    "form-TOTAL_FORMS": "3",
                                    "form-INITIAL_FORMS": "0",
                                    "form-MAX_NUM_FORMS": "",

                                    "form-0-description": "oridinateur",
                                    "form-0-quantity": "80",
                                    "form-0-price": "1000",

                                    "form-1-description": "",
                                    "form-1-quantity": "",
                                    "form-1-price": "",

                                    "form-2-description": "",
                                    "form-2-quantity": "",
                                    "form-2-price": "",

                                    "add_invoice": "Enregistrer",
                                    }
                                    )
        self.assertRedirects(response1,\
                            "http://testserver/?next=/add_invoice/")

        # On test la views modification de facture
        response = self.logged_user.post('/modification/1', {
                                    "client": client.id,
                                    "tax": "on", "number": "8",
                                    "date": "25/10/2010",
                                    "subject": "vente",
                                    "location": "Bamako",
                                    "type": "Facture",
                                    "tax_rate": "18",

                                    "form-TOTAL_FORMS": "3",
                                    "form-INITIAL_FORMS": "0",
                                    "form-MAX_NUM_FORMS": "",

                                    "form-0-description": "Asus Pentuim M",
                                    "form-0-quantity": "1",
                                    "form-0-price": "400000",

                                    "form-1-description": "Toshiba",
                                    "form-1-quantity": "1",
                                    "form-1-price": "3500000",

                                    "form-2-description": "",
                                    "form-2-quantity": "",
                                    "form-2-price": "",

                                    "add_invoice": "Enregistrer",
                                    })
        invoice = Invoice.objects.get(id=2)
        invoiceitem = InvoiceItem.objects.get(id=2)
        self.assertEqual(invoice.__unicode__(),
                         "8 - Alou-services : vente")
        item = invoice.invoiceitem_set.values()[0]
        self.assertEqual(item['price'], 400000)
        self.assertEqual(item['quantity'], 1)
        self.assertEqual(item['description'], "Asus Pentuim M")

        self.assertEqual(invoiceitem.__unicode__(),
                         "Asus Pentuim M 1 400000")

        # On test la views modification de facture sans etre identifier
        response1 = self.anonymous_client.post('/modification/1', {
                            "client": client.id,
                            "tax": "on", "number": "8",
                            "date": "25/10/2010",
                            "subject": "vente d'ordi",
                            "location": "Bamako",
                            "type": "Facture",
                            "tax_rate": "18",

                            "form-TOTAL_FORMS": "3",
                            "form-INITIAL_FORMS": "0",
                            "form-MAX_NUM_FORMS": "",

                            "form-0-description": "oridinateur",
                            "form-0-quantity": "80",
                            "form-0-price": "1000",

                            "form-1-description": "",
                            "form-1-quantity": "",
                            "form-1-price": "",

                            "form-2-description": "",
                            "form-2-quantity": "",
                            "form-2-price": "",

                            "add_invoice": "Enregistrer",
                            }
                            )
        self.assertRedirects(response1,\
                              "http://testserver/?next=/modification/1")

    def test_view_add_organization(self):
        """
            test la vue ajout d'organisation
        """
        from fact.models import Organization

        # On test la views ajout oorganization
        response = self.logged_user.post('/add_organization/', {
                                    'name': u"fadiga et fils",
                                    'owner': 'Dolo',
                                    'address': 'Boulkassoumbougou',
                                    'address_extra': 'hippodrome',
                                    'address_extra2': 'kati ',
                                    'legal_infos': 'koko'}, \
                                    )

        organization = Organization.objects.get(id=1)
        self.assertEqual(organization.__unicode__(), "fadiga et fils")
        self.assertEqual(organization.name, "fadiga et fils")
        self.assertEqual(organization.owner.username, "Dolo")
        self.assertEqual(organization.legal_infos, "koko")

        # On test la views ajout oorganization sans etre identifier
        response1 = self.anonymous_client.post('/add_organization/', {
                                    'name': u"fadiga et fils",
                                    'owner': 'fad',
                                    'address': 'Boulkassoumbougou',
                                    'address_extra': 'hippodrome',
                                    'address_extra2': 'kati ',
                                    'legal_infos': 'koko'}
                                    )

        self.assertRedirects(response1,\
                           "http://testserver/?next=/add_organization/")

        # On test la views edit oorganization
        response = self.logged_user.post('/edit_organization/', {
                                    'name': u"fad  service",
                                    'owner': 'fad',
                                    'address': 'ACI rue 580',
                                    'address_extra': 'hippodrome',
                                    'address_extra2': 'kati ',
                                    'legal_infos': 'koko'})
        organization = Organization.objects.get(id=1)
        self.assertEqual(organization.__unicode__(), "fad  service")

        # On test la views edit oorganization sans etre identifier
        response1 = self.anonymous_client.post('/edit_organization/', {
                                    'name': u"fad  service",
                                    'owner': 'fad',
                                    'address': 'ACI rue 580',
                                    'address_extra': 'hippodrome',
                                    'address_extra2': 'kati ',
                                    'legal_infos': 'koko'})
        self.assertRedirects(response1,\
                         "http://testserver/?next=/edit_organization/")


class SimpleTest(TestCase):

    def setUp(self):
        from fact.models import Organization, Owner, Client

        # On crée un Owner
        self.own = Owner.objects.create(first_name=u"John",\
                                        last_name="Doe")

        # On cre une Organization
        self.org = Organization.objects.create(name="Coucou",\
                                               owner=self.own)

        # On cre un client
        self.client = Client.objects.create(name=u"Ploupe",\
                                            organization=self.org)

    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.failUnlessEqual(1 + 1, 2)

    def test_client(self):
        """
            test model client
        """
        self.assertEqual(self.client.__unicode__(), "Ploupe")

    def test_owner(self):
        """
            test model owner
        """
        self.assertEqual(self.org.owner, self.own)

    def test_organization(self):
        """
            test model organization
        """
        self.assertEqual(self.org.__unicode__(), u"Coucou")

    def test_invoice(self):
        """
            test model invoice
        """
        from fact.models import Invoice, Client, InvoiceItem
        # On crée et test invoice
        inv = Invoice.objects.create(organization=self.org,
                                     number=1, type=Invoice.TYPE_PROF,
                                     client=self.client)
        self.assertEqual(inv.__unicode__(), u"1 - Coucou : ")
        #on crée et test invoiceitem
        item = InvoiceItem.objects.create(description="moto",
                                           quantity=4, price=1000,
                                           invoice=inv)
        self.assertEqual(item.__unicode__(), u"moto 4 1000")

    def test_get_next_number(self):
        """
            test invoice get_next_number function
        """
        from fact.models import Invoice
        inv = Invoice.objects.create(organization=self.org, number=1,\
                                     type=Invoice.TYPE_PROF,
                                     client=self.client)
        self.assertEqual(Invoice.get_next_number(org=self.org), 2)

        inv = Invoice.objects.create(organization=self.org, number=1295,\
                                     type=Invoice.TYPE_PROF,
                                     client=self.client)
        self.assertEqual(Invoice.get_next_number(org=self.org), 1296)


'''__test__ = {"doctest": """
Another way to test that 1 + 1 is equal to 2.
#~ #~
>>> 1 + 1 == 2
True
"""}
'''
