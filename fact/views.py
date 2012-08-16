#!/usr/bin/env python
# -*- coding= UTF-8 -*-
import os
import reportlab

from reportlab.pdfgen import canvas
from cStringIO import StringIO

from django.shortcuts import (render_to_response,
                              HttpResponseRedirect, redirect)
from django.http import HttpResponse, QueryDict
from django.core.urlresolvers import reverse
from django.core.context_processors import csrf
from datetime import date
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.db import IntegrityError
from django.core.paginator import Paginator, EmptyPage
from django.utils.translation import ugettext, ugettext_lazy as _
from django.utils.datastructures import MultiValueDictKeyError

import os, sys
import Image


from cel import cel
from form import (InvoiceForm, InvoiceItemform, AddOrganization,
                  ClientForm, LoginForm, AddOwner, Owner_editForm,
                  ModifInvoiceForm, HeaderForm, ImagesForm)
from django.forms.formsets import formset_factory
from django.contrib.auth import (authenticate, login as django_login,
                                 logout as django_logout)

from django.contrib.auth.models import Group
from fact.models import *
from django.core.files import File


def my_custom_404_view(request):
    """
    """
    return render_to_response('404.html', {})


@login_required
def owner(request):
    """create an url by owner
    """
    group_users = ''
    try:
        # on recupere le groupe de l'utilisateur connecté
        group_users = request.user.groups.values_list()
    except IndexError:
        pass

    grp = group_users[0][1]
    if grp.__eq__("admin"):

        user = request.user
        owners = Owner.objects.all()
        #On cree l'url de chaque utilisateur.
        for owner in owners:
            owner.url = reverse('owner_edit', args=[owner.id])
        c = ({'owners': owners, 'user': user})
        return render_to_response('owner.html', c)
    else:
        return redirect('dashboard')


@login_required
def add_client(request):
    """ add a client """
    # on recupere l'utilisateur connecté
    user = request.user
    # on recupere l'organisation de l'utilisateur connecté
    org = Organization.objects.filter(owner=request.user.id)[0]

    c = {}
    c.update(csrf(request))
    c.update({'user': user, 'organization': org})
    if request.method == 'POST':

        # On charge le formulaire en lui passant comme paramettre
        # la requette POST.
        form = ClientForm(request, request.POST)
        c.update({'form': form})
        client = Client.objects.filter(name=request.POST['name'],\
                                       address=request.POST['address'])
        if client:
            c.update({'error': 'ce client existe deja'})
        else:
            if form.is_valid():
                form.save()
                clients = Client.objects.filter(organization=org)
                last_client = clients.latest('id')
                request.session['last_client'] = last_client
                return HttpResponseRedirect(reverse('add_invoice'))
    else:
        form = ClientForm(request=request)
        c.update({'form': form})
    return render_to_response('add_client.html', c)


@login_required
def add_owner(request):
    """ add owner
    """
    group_users = ''
    try:
        # on recupere le groupe de l'utilisateur connecté
        group_users = request.user.groups.values_list()
    except IndexError:
        pass

    grp = group_users[0][1]
    if grp.__eq__("admin"):

        c = {}
        c.update(csrf(request))
        form = AddOwner(request=request)
        user = request.user
        c.update({'form': form, 'user': user,\
                                'erreur': "Ce champ est obligatoire."})

        if request.method == 'POST':

            #On charge le formulaire en lui passant comme
            #paramettre la requette POST.
            form = AddOwner(request, request.POST)
            c.update({'form': form})

            if request.POST.get('password') != request.POST.\
                                            get('password_confirmation'):
                c.update({'error': "Les mots de passe sont diffirents"})

            if request.POST.get('email') == "":
                e_mail = 'aucun@email.ml'
            else:
                e_mail = request.POST.get('email')
            if form.is_valid():
                if request.POST.get('password') == request.POST.\
                                            get('password_confirmation'):
                    username = request.POST.get('username')
                    password = request.POST.get('password')
                    email = e_mail

                    #On oblige l'utilisateur connecter a
                    #remplir tous les champs.
                    if username != ''and password != '' and email != '' \
                                     and request.POST.get('first_name') != ''\
                                     and request.POST.get('last_name') != '':
                        try:
                            user = User.objects.\
                                       create_user(username,\
                                                    email, password)
                        except IntegrityError:
                            c.update({'error': "le nom d'utilisateur\
                                       existe deja"})
                            return render_to_response('add_owner.html', c)

                        user.is_staff = request.POST.get('is_staff')
                        user.is_active = request.POST.get('actif')

                        if user.is_active:
                            user.first_name = request.POST.get('first_name')
                            user.last_name = request.POST.get('last_name')
                            user.is_staff = True
                            user.is_active = True
                            user.groups.add(Group.objects.get(id=2))
                            user.save()

                        else:
                            user.first_name = request.POST.get('first_name')
                            user.last_name = request.POST.get('last_name')
                            user.is_staff = False
                            user.is_active = False
                            user.groups.add(Group.objects.get(id=2))
                            user.save()

                        #On instancie un owner et on le cree a partir des
                        #informations utilises pour creer le user.
                        owner = Owner(User)
                        owner.id = user.id
                        owner.is_staff = user.is_staff
                        owner.is_active = user.is_active
                        owner.first_name = user.first_name
                        owner.last_name = user.last_name
                        owner.username = user.username
                        owner.password = user.password
                        owner.is_active = True
                        #~ for group in request.POST.getlist('groupe'):
                            #~ owner.groups.add(Group.objects.get(id=group))
                        owner.save()
                        return HttpResponseRedirect(reverse(\
                                                        'add_organization'))

        return render_to_response('add_owner.html', c)
    else:
        return redirect('dashboard')


@login_required
def owner_edit(request, *args, **kwargs):
    """ edit an organization
    """
    c = {}
    c.update(csrf(request))
    owner_id = kwargs["id"]
    selected_owner = Owner.objects.get(id=owner_id)
    groupes = selected_owner.groups.add(Group.objects.get(id=2))

    dict_ = {"username": selected_owner.username, \
            "password": selected_owner.password, \
            "password_confirmation": selected_owner.password, \
            "last_name": selected_owner.last_name, \
            "first_name": selected_owner.first_name,\
            "email": selected_owner.email,\
            "actif": selected_owner.is_active,\
            "groupe": "utilisateur"
            }

    form = Owner_editForm(dict_)
    user = request.user
    c.update({'form': form, 'user': user,\
                            'selected_owner': selected_owner,\
                            'erreur': "Ce champ est obligatoire."})

    if request.method == 'POST':
        #On charge le formulaire en lui passant comme paramettre
        #la requette POST.
        form = Owner_editForm(request.POST)
        c.update({'form': form})
        if request.POST.get('password') != request.\
                   POST.get('password_confirmation'):
            c.update({'error': "Les mots de passe sont diffirents"})

        if request.POST.get('email') == "":
            e_mail = 'aucun@email.ml'
        else:
            e_mail = request.POST.get('email')
        if form.is_valid():
            if request.POST.get('password') == request.\
                       POST.get('password_confirmation'):
                selected_owner.username = request.POST.get('username')
                selected_owner.password = request.POST.get('password')
                selected_owner.last_name = request.POST.get('last_name')
                selected_owner.first_name = request.POST.\
                                                    get('first_name')
                selected_owner.email = e_mail
                selected_owner.is_active = request.POST.get('actif')
                selected_owner.groups.add(Group.objects.get(id=2))
                selected_owner.save()
                return HttpResponseRedirect(reverse('owner'))
    return render_to_response('owner_edit.html', c)


def login(request):
    """
        login est la views qui permet de se connecter
    """
    if request.user.is_authenticated():
        try:
            if request.user.\
                       groups.values_list()[0][1] in \
                                            ['admin']:
                return redirect('owner')

            if request.user.\
                      groups.values_list()[0][1] in \
                                        ['utilisateur']:
                return redirect('dashboard')
        except IndexError:
            raise Http404
    else:
        c = {}
        c.update(csrf(request))
        state = ugettext("Se connecter")
        #Initialise username et password à vide

        username = password = ''

        # On appel la fonction LoginForm() dans le formulaire

        form = LoginForm()
        c = ({'form': form})

        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            url = request.GET.get('next')
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    django_login(request, user)
                    state = ugettext("Interconnection of good!")
                    if url:
                        return HttpResponseRedirect(request, url)
                    else:
                        try:
                            if request.user.\
                                       groups.values_list()[0][1] in \
                                                            ['admin']:
                                return redirect('owner')

                            if request.user.\
                                      groups.values_list()[0][1] in \
                                                        ['utilisateur']:
                                return redirect('dashboard')
                        except IndexError:
                            raise Http404
                else:
                    state = ugettext("Your Account is not active,\
                                    please contact the site admin.")
            else:
                state = ugettext(u"Votre nom d'utilisateur et / ou \
                                votre mot de passe est incorrect. \
                                Veuillez réessayer.")
        c.update({"user": request.user, 'state': state})

        c.update(csrf(request))
        return render_to_response('login.html', c)


def logout(request):
    """
        logout est la views qui permet de se deconnecter
    """

    django_logout(request)
    return redirect("/")


@login_required
def dashboard(request, *args, **kwargs):
    """ display all invoices by user """

    # on recupere le numero depuis l'url si le numero
    # est none on donne 1 par  defaut
    num = kwargs["num"] or 1

    user = request.user

    try:
        if request.GET['display'] == 'facture':
            title_page = 'FACTURES'
            link_page = 'facture'
            invoices = Invoice.objects.\
                                filter(organization__owner=request.user,\
                                type='Facture').order_by('-number')
        elif request.GET['display'] == 'proforma':
            title_page = 'PROFORMAS'
            link_page = 'proforma'
            invoices = Invoice.objects.\
                               filter(organization__owner=request.user,\
                                    type='Proforma').order_by('-number')
        else:
            title_page = 'TOUTES'
            link_page = 'facture ou proforma'
            invoices = Invoice.objects.\
                               filter(organization__owner=request.user).\
                               order_by('-number')

    except MultiValueDictKeyError:
        title_page = 'TOUTES'
        link_page = 'facture ou proforma'
        invoices = Invoice.objects.\
                           filter(organization__owner=request.user).\
                           order_by('-number')

    for invoice in invoices:
        # on constitue l'url du lien pointant sur la vue de la
        # duplication de la facture
        invoice.url_duplicate = reverse('duplicate',
                                         args=[invoice.id])
        invoice.url_delete_confirm = reverse('delete_confirm',
                                              args=[invoice.id])
        # on constitue l'url du lien pointant sur la vue qui affiche
        # la facture en integralité.
        invoice.url_show_invoice = reverse('show_invoice',
                                            args=[invoice.id])
        invoice.url_modification = reverse('modification',
                                            args=[invoice.id])
        invoice.url_pdf = reverse('PDF_invoice_done',
                                            args=[invoice.id])
    paginator = Paginator(invoices, 30)

    page = paginator.page(int(num))
    # si le numero de la page est 2
    page.is_before_first = (page.number == 2)
    # si le numero de la page est egale au numero de l'avant
    # derniere page
    page.is_before_last = (page.number == paginator.num_pages - 1)
    # on constitue l'url de la page suivante
    page.url_next = reverse('dashboard', args=[int(num) + 1])
    # on constitue l'url de la page precedente
    page.url_previous = reverse('dashboard', args=[int(num) - 1])
    # on constitue l'url de la 1ere page
    page.url_first = reverse('dashboard')
    # on constitue l'url de la derniere page
    page.url_last = reverse('dashboard',
                            args=[paginator.num_pages])

    ctx = {'user': user,
           'paginator': paginator,
           'page': page,
           'title_page': title_page,
           'link_page': link_page}

    ctx.update(csrf(request))

    if len(invoices) > 10:
        drapo = 'oui'
        ctx.update({'drapo': drapo})
    return render_to_response('dashboard.html', ctx)


@login_required
def modification(request, *args, **kwargs):
    """ modify """
    c = data = {}
    cptr = 0
    try:
        org = Organization.objects.get(owner__pk=request.user.pk)
    except Organization.DoesNotExist:
        return HttpResponseRedirect(reverse('add_organization'))
    num = kwargs["num"] or 1
    invoice_edit = Invoice.objects.get(id=num)
    items = invoice_edit.invoiceitem_set.all()
    n = len(items)
    # envoie du type de la facture
    c.update({'type': invoice_edit.type})

    if request.method == 'GET':
        item_number_ = n
    else:
        item_number_ = int(request.POST['form-TOTAL_FORMS'])

    for item in items:
        data["form-%d-invoice" % cptr] = invoice_edit.id
        data["form-%d-price" % cptr] = item.price
        data["form-%d-quantity" % cptr] = item.quantity
        data["form-%d-description" % cptr] = item.description
        cptr = cptr + 1
    if 'add_item_' in request.POST:

        #Incremente le nombre total d'item si Add_item est utilisé
        item_number_ += 1
        #Copie de la requete post pour pouvoir modifier le contenu
        addtional_item_ = request.POST.copy()
        #Modification du nombre total d'tem
        addtional_item_.update({'form-TOTAL_FORMS': item_number_})
        for item in addtional_item_:
            try:
                data["form-%d-price" % cptr] = \
                                    addtional_item_["form-%d-price"\
                                     % cptr]
                data["form-%d-quantity" % cptr] = \
                                    addtional_item_["form-%d-quantity"\
                                    % cptr]
                data["form-%d-description" % cptr] =\
                                  addtional_item_["form-%d-description"\
                                  % cptr]

            except MultiValueDictKeyError:
                data["form-%d-price" % cptr] = u""
                data["form-%d-quantity" % cptr] = u""
                data["form-%d-description" % cptr] = u""
            cptr = cptr + 1

    dict = {'type': invoice_edit.type,
            'tax_rate': invoice_edit.tax_rate,
            'tax': invoice_edit.tax,
            'subject': invoice_edit.subject,
            'location': invoice_edit.location,
            'client': invoice_edit.client.id,
            'number': invoice_edit.number,
            'date': invoice_edit.date}

    InvoiceItemFormSet = formset_factory(InvoiceItemform,\
                                         extra=item_number_)

    data.update({'form-TOTAL_FORMS': item_number_,
            'form-INITIAL_FORMS': u'2',
            'form-MAX_NUM_FORMS': u'',
            })

    if 'add_invoice' in request.POST and request.method == 'POST':
        try:
            formset = InvoiceItemFormSet(request.POST, addtional_item)
            form = InvoiceForm(request, request.POST, addtional_item)
        except:
            formset = InvoiceItemFormSet(request.POST)
            form = InvoiceForm(request, request.POST)
        # on verifie si le bouton cliqué est celui de add_invoice
        if 'add_invoice' in request.POST:
            # on verifie si le form et le formset sont valides
            if form.is_valid() and formset.is_valid():

                # on sauvegarde la facture avec ses items
                invoice = form.save()
                for f in formset.forms:
                    if f.cleaned_data:
                        item = f.save(commit=False)
                        item.invoice = invoice
                        item.save()
                invoice_del = Invoice.objects.\
                                      filter(number=invoice.number).\
                                      order_by('id')[0]
                items_del = invoice_del.invoiceitem_set.all()
                items_del.delete()
                invoice_del.delete()

                return HttpResponseRedirect(reverse('invoice_done'))

    else:
        form = InvoiceForm(request, dict)
        formset = InvoiceItemFormSet(data)

    c.update({'formset': formset, 'form': form, 'organization':\
                                          org, 'valide': 'send'})
    c.update(csrf(request))

    return render_to_response("modification.html", c)


@login_required
def duplicate(request, *args, **kwargs):
    """duplicate invoice for edit """

    num = kwargs["id"] or 1
    invoice_copy = Invoice.objects.get(id=num)
    items = invoice_copy.invoiceitem_set.all()

    invoice_copy.id = None
    invoice_copy.pk = None
    number = Invoice.get_next_number(invoice_copy.organization)
    invoice_copy.number = number
    invoice_copy.subject = "Copie de %s" % invoice_copy.subject
    invoice_copy.save()

    for item in items:
        item.id = None
        item.pk = None
        item.invoice = invoice_copy
        item.save()

    return HttpResponseRedirect(reverse('dashboard'))


@login_required
def delete_confirm(request, *args, **kwargs):
    """ ask confirmation for deleting """

    user = request.user
    num = kwargs["id"] or 1
    # on recupere la facture a supprimer
    invoice = Invoice.objects.get(id=num)
    url = reverse('delete', args=[invoice.id])
    ctx = {'invoice': invoice, 'url': url, 'user': user}

    return render_to_response('delete.html', ctx)


@login_required
def delete(request, *args, **kwargs):
    """ delete an invoice """

    user = request.user
    num = kwargs["id"]
    invoice = Invoice.objects.get(id=num)
    invoice.invoiceitem_set.all().delete()
    invoice.delete()
    return HttpResponseRedirect(reverse('dashboard'))


@login_required
def add_organization(request, *args, **kwargs):
    """ add a new organization """

    #On recupere l'id de l'image choisit
    num = kwargs["id"] or 1
    org_image = ""
    try:
        org_image = Images.objects.get(id=num)
    except:
        pass

    # on verifie si le bouton cliqué est celui de add_logo
    if 'add_logo' in request.POST:
        # on sauvegarde une copie de la requette post dans la
        # requette session et on supprime le nom du bouton
        # add_logo de cette copie
        request.session['create_organization'] = request.POST.copy()

        # puis on redige sur la vue add_logo
        return HttpResponseRedirect(reverse('choose_logo_addorg'))

    owners = Owner.objects.all()
    owner_to_edit = owners.latest('id')
    #On charge le formulaire.
    form = AddOrganization(initial={'owner_id': owner_to_edit.id})
    user = request.user
    #On initialise un dictionnaire vide
    dict_org = {}

    #On verifie si il ya des valeurs dans le request.session
    if 'create_organization' in request.session.keys():
        #On cree un dictionnaire qui retiendra les valeurs dejas saisie
        #  par l'utilisateur.
        dict_org = {'name': request.session['create_organization']['name'],
                    'image': org_image,
                'address': request.session['create_organization']['address'],\
                    'address_extra':\
                    request.session['create_organization']['address_extra'],
                    'address_extra2':\
                    request.session['create_organization']['address_extra2'],\
                    'legal_infos':\
                    request.session['create_organization']['legal_infos'],\
                    'owner_id': owner_to_edit.id}
        #On charge le formulaire avec les donnees du dictionnaire.
        form = AddOrganization(dict_org)
        #On suprime les infos de l'entrprise de la memoire
        request.session.pop('create_organization')

    c = {'form': form, "user": request.user}
    c.update(csrf(request))

    #On instatancie un objet organisation
    organization = Organization()

    if request.method == 'POST':
        if request.POST["name"] == "":
            erreur_organization_name = "Veillez indiquer un nom \
                                        d'organization s.v.p."
            c.update({"erreur_organization_name":\
                      erreur_organization_name})
            return render_to_response('add_organization.html', c)
        elif request.POST["address"] == "":
            erreur_address = "Veillez indiquer une addresse s.v.p."
            c.update({"erreur_address": erreur_address})
            return render_to_response('add_organization.html', c)
        else:
            #On renseigne les differents champs de organisation avec les
            # donnees de request.POST
            organization.name = request.POST.get('name')
            #On verifie si l'utilisateur a choisit une image.
            #si non, on enregistre quand meme l'organisation.
            try:
                organization.image = org_image
            except ValueError:
                pass
            organization.address = request.POST.get('address')
            organization.address_extra = request.POST.\
                                                get('address_extra')
            organization.address_extra2 = request.POST.\
                                                get('address_extra2')
            organization.legal_infos = request.POST.get('legal_infos')
            organization.owner_id = owner_to_edit.id
            #On sauve.
            organization.save()
        return HttpResponseRedirect(reverse('owner'))
    return render_to_response('add_organization.html', c)


@login_required
def edit_organization(request, *args, **kwargs):
    """ edit an organization """

    user = request.user
    if kwargs["id"]:
        #On recupere l'id de l'image choisit
        num = kwargs["id"] or 1
        org_image = Images.objects.get(id=num)
    # on verifie si le bouton cliqué est celui de add_logo
    if 'add_logo' in request.POST:
        # on sauvegarde une copie de la requette post dans la
        # requette session et on supprime le nom du bouton
        # add_logo de cette copie
        request.session['create_organization'] = request.POST.copy()

        # puis on redige sur la vue add_logo
        return HttpResponseRedirect(reverse('choose_logo_editorg'))

    #On recupere l'organisation ayant l'id recuperer.
    try:
        org_to_edit = Organization.objects.get(owner=request.user.id)
    except Organization.DoesNotExist:
        return HttpResponseRedirect(reverse('add_organization'))

    try:
        #On cree un dictionnaire contenant les valeurs des champs de
        #l'organisation
        dict_org = {'name': org_to_edit.name,
                    'image': org_to_edit.image,
                    'address': org_to_edit.address,
                    'address_extra': org_to_edit.address_extra,
                    'address_extra2': org_to_edit.address_extra2,
                    'legal_infos': org_to_edit.legal_infos,\
                    'owner_id': request.user.id}
        #Si la requette.session n'est pas vide, on change la valeur de l'image
        if 'create_organization' in request.session.keys():
            #On change la valeur image du dictionnaire contenant les valeurs
            # des champs de l'organisation
            dict_org["image"] = org_image
            #On suprime les infos de l'entrprise de la memoire
            request.session.pop('create_organization')

    except:
        blank_picture = Images()
        #On cree un dictionnaire contenant les valeurs des
        # champs de l'organisation
        dict_org = {'name': org_to_edit.name,
                    'image': blank_picture,
                    'address': org_to_edit.address,
                    'address_extra': org_to_edit.address_extra,
                    'address_extra2': org_to_edit.address_extra2,
                    'legal_infos': org_to_edit.legal_infos,\
                    'owner_id': request.user.id}

    #On charge le formulaire avec le dictionnaire cree.
    form = AddOrganization(dict_org)
    c = {'form': form, "user": request.user}
    c.update(csrf(request))

    if request.method == 'POST':
        if request.POST["name"] == "":
            erreur_organization_name = "Veillez indiquer un nom \
                                        d'entreprise s.v.p."
            c.update({"erreur_organization_name":\
                        erreur_organization_name})
            return render_to_response('edit_organization.html', c)
        elif request.POST["address"] == "":
            erreur_address = "Veillez indiquer une addresse s.v.p."
            c.update({"erreur_address": erreur_address})
            return render_to_response('edit_organization.html', c)
        else:
            #On renseigne les differents champs de organisation avec
            # les donnees de request.POST
            org_to_edit.name = request.POST.get('name')
            #On verifie si l'utilisateur a choisit une image.
            #si non, on enregistre quand meme l'organisation.
            try:
                org_to_edit.image = org_image
            except UnboundLocalError:
                pass
            org_to_edit.address = request.POST.get('address')
            org_to_edit.address_extra = request.POST.\
                                                get('address_extra')
            org_to_edit.address_extra2 = request.POST.\
                                                get('address_extra2')
            org_to_edit.legal_infos = request.POST.get('legal_infos')
            org_to_edit.owner_id = request.user.id

            #On sauvegarde.
            org_to_edit.save()
        return HttpResponseRedirect(reverse('dashboard'))
    return render_to_response('edit_organization.html', c)


@login_required
def choose_logo_editorg(request, *args, **kwargs):
    """ delete an invoice """

    num = kwargs["num"] or 1
    form = ImagesForm()
    if request.POST:
        logo = Images()
        logo.name = request.FILES['name']
        logo.save()

    user = request.user
    c = {"user": request.user}
    c.update(csrf(request))

    #On charge les images du dossier qui contient les images.
    img = Images.objects.all()
    #A chaque objet image, on attribue un url.
    for image in img:
        image.url = reverse('edit_organization', args=[image.id])

    paginator = Paginator(img, 1)
    page = paginator.page(int(num))
    # si le numero de la page est 2
    page.is_before_first = (page.number == 2)
    # si le numero de la page est egale au numero de l'avant
    # derniere page
    page.is_before_last = (page.number == paginator.num_pages - 1)
    # on constitue l'url de la page suivante
    page.url_next = reverse('choose_logo_editorg', args=[int(num) + 1])
    # on constitue l'url de la page precedente
    page.url_previous = reverse('choose_logo_editorg', args=[int(num) - 1])
    # on constitue l'url de la 1ere page
    page.url_first = reverse('choose_logo_editorg')
    # on constitue l'url de la derniere page
    page.url_last = reverse('choose_logo_editorg',
                            args=[paginator.num_pages])

    c.update({'img': img, "form": form, 'paginator': paginator, "page": page})

    return render_to_response('choose_logo.html', c)


@login_required
def choose_logo_addorg(request, *args, **kwargs):
    """ delete an invoice """

    num = kwargs["num"] or 1
    form = ImagesForm()
    user = request.user

    image_ = Images()
    c = {"user": request.user}
    c.update(csrf(request))
    #On charge les images du dossier qui contient les images.
    img = Images.objects.all()
    #A chaque objet image, on attribue un url.
    for image in img:
        image.url = reverse('add_organization', args=[image.id])

    if request.method == 'POST':
        form = ImagesForm(request.POST, request.FILES)
        if form.is_valid():

            if request.FILES['name']:
                image_.name = request.FILES['name']
                image_.save()
            return HttpResponseRedirect(reverse('choose_logo_addorg'))

    paginator = Paginator(img, 1)
    page = paginator.page(int(num))
    # si le numero de la page est 2
    page.is_before_first = (page.number == 2)
    # si le numero de la page est egale au numero de l'avant
    # derniere page
    page.is_before_last = (page.number == paginator.num_pages - 1)
    # on constitue l'url de la page suivante
    page.url_next = reverse('choose_logo_addorg', args=[int(num) + 1])
    # on constitue l'url de la page precedente
    page.url_previous = reverse('choose_logo_addorg', args=[int(num) - 1])
    # on constitue l'url de la 1ere page
    page.url_first = reverse('choose_logo_addorg')
    # on constitue l'url de la derniere page
    page.url_last = reverse('choose_logo_addorg',
                            args=[paginator.num_pages])

    c.update({'img': img, "form": form, 'paginator': paginator, "page": page})

    return render_to_response('choose_logo.html', c)


@login_required
def add_invoice(request, *args, **kwargs):
    """add a new invoice"""
    formset_data = {}

    c = {"user": request.user}
    cptr = 0
    addtional_item = ""

    try:
        org = Organization.objects.get(owner__pk=request.user.pk)

    except Organization.DoesNotExist:
        return HttpResponseRedirect(reverse('add_organization'))
    # initilisation du nombre d'item
    try:
        item_number = int(request.POST['form-TOTAL_FORMS'])
    except:
        item_number = 3

    if 'add_item' in request.POST or 'add_client' in request.POST:
        #Incremente le nombre total d'item si Add_item est utilisé
        item_number += 1
        #Copie de la requete post pour pouvoir modifier le contenu
        addtional_item = request.POST.copy()
        #Modification du nombre total d'tem
        addtional_item.update({'form-TOTAL_FORMS': item_number})

        formset_data = {'form-TOTAL_FORMS': item_number,
                        'form-INITIAL_FORMS': u'2',
                        'form-MAX_NUM_FORMS': u''
                        }

        for item in addtional_item:
            try:
                formset_data["form-%d-price" % cptr] = \
                             addtional_item["form-%d-price" % cptr]
                formset_data["form-%d-quantity" % cptr] = \
                             addtional_item["form-%d-quantity" % cptr]
                formset_data["form-%d-description" % cptr] =\
                             addtional_item["form-%d-description" % cptr]
            except MultiValueDictKeyError:
                formset_data["form-%d-price" % cptr] = u""
                formset_data["form-%d-quantity" % cptr] = u""
                formset_data["form-%d-description" % cptr] = u""
            cptr = cptr + 1

        header = {
                    'type': addtional_item["type"],
                    'tax_rate': addtional_item["tax_rate"],
                    'location': addtional_item["location"],
                    'number': addtional_item["number"],
                    'client': addtional_item["client"],
                    'date': addtional_item["date"]
                 }

    InvoiceItemFormSet = formset_factory(InvoiceItemform,\
                                         extra=item_number)
    client = ''
    # on verifie si last_client est dans la requette session
    if 'last_client' in request.session:
        # on enleve la valeur de last_client et on le met dans client
        client = request.session.pop('last_client')

    try:
        if request.GET['display'] == 'facture':
            link_page = 'Facture'
            c.update({"link_page": link_page})
        if request.GET['display'] == 'proforma':
            link_page1 = 'Proforma'
            c.update({"link_page1": link_page1})
    except:
        pass

    if  'add_invoice' in request.POST and request.method == 'POST':

        try:
            formset = InvoiceItemFormSet(request.POST, addtional_item)
            form = InvoiceForm(request, request.POST, addtional_item)
        except:
            formset = InvoiceItemFormSet()
            form = InvoiceForm(request)
        # on verifie si le bouton cliqué est celui de add_invoice
        if 'add_invoice' in request.POST:

            # on verifie si le form et le formset sont valides
            if form.is_valid() and formset.is_valid():
                # on sauvegarde la facture avec ses items
                invoice = form.save()
                for f in formset.forms:
                    if f.cleaned_data:
                        item = f.save(commit=False)
                        item.invoice = invoice
                        item.save()
                return HttpResponseRedirect(reverse('invoice_done'))
    else:
        if 'add_item' in request.POST:
            form = HeaderForm(header)
            formset = InvoiceItemFormSet(formset_data)
            c.update({'valide': 'send'})
        else:
            form = InvoiceForm(request=request)
            formset = InvoiceItemFormSet()

    # on verifie si create_invoice_data est dans la requette session
    if 'create_invoice_data' in request.session and \
        'nouveau' not in request.POST:

        # on enleve la valeur de create_invoice_data et on le met
        # dans request.POST
        request.POST = request.session.pop('create_invoice_data')
        # on verifie si il a crée un nouveau client
        if client:
            # on met le nouveau client dans requette post
            request.POST['client'] = client.id
        request.method = 'POST'
        if request.method == 'POST':
            form = InvoiceForm(request, request.POST)
            formset = InvoiceItemFormSet(request.POST)
        c.update({'valide': 'send'})
    # on verifie si le bouton cliqué est celui de add_client
    if 'add_client' in request.POST:
        # on sauvegarde une copie de la requette post dans la
        # requette session et on supprime le nom du bouton
        # add_client de cette copie
        request.session['create_invoice_data'] = request.POST.copy()
        request.session['create_invoice_data'].pop('add_client')
        # puis on redige sur la vue add_client
        return HttpResponseRedirect(reverse('add_client'))

    c.update({'formset': formset, 'form': form, 'organization': org})
    c.update(csrf(request))

    return render_to_response("invoiceitem.html", c)


@login_required
def invoice_done(request, *args, **kwargs):
    """ display the invoice done """

    user = request.user
    try:
        last_invoice = Invoice.objects.\
                            filter(organization__owner=request.user).\
                            order_by('-id')[0]
        url = reverse('PDF_invoice_done', args=[last_invoice.id])

    except IndexError:
        raise Http404

    invoiceitems = InvoiceItem.objects.filter(invoice=last_invoice.id)
    try:
        dict_header = {'date': last_invoice.date, \
                      'number': last_invoice.number,\
                      'location': last_invoice.location,\
                      'subject': last_invoice.subject,\
                      'type': last_invoice.type,\
                      'client': last_invoice.client.name,\
                      'organization': last_invoice.organization,\
                      'tax': last_invoice.tax,\
                      'tax_rate': last_invoice.tax_rate,\
                      'logo': last_invoice.organization.image
                      }
    except:
        blank_picture = Images()
        dict_header = {'date': last_invoice.date, \
                      'number': last_invoice.number,\
                      'location': last_invoice.location,\
                      'subject': last_invoice.subject,\
                      'type': last_invoice.type,\
                      'client': last_invoice.client.name,\
                      'organization': last_invoice.organization,\
                      'tax': last_invoice.tax,\
                      'tax_rate': last_invoice.tax_rate,\
                      'logo': blank_picture
                      }

    ctx = {'invoice': invoiceitems,
           'dict_header': dict_header,
           'user': user, 'url': url}
    lists, ht, comp = [], 0, 10

    for i in invoiceitems:
        dic = {}
        dic['description'] = i.description
        dic['quantity'] = i.quantity
        dic['price'] = i.price
        dic['montant'] = i.price * i.quantity
        comp -= comp
        ht += dic['montant']
        lists.append(dic)

    nb = 10 - len(lists)
    while nb != 0:
        nb = nb - 1
        lists.append({})
    ctx.update({'lists': lists, 'ht': ht})

    # On  effectue le operations avec les valeurs de l'utisateur
    #On passe le montant total au fonction cel() qui permet de le
    # convertir en lettre
    ht_en_lettre = cel(ht)

    if dict_header['tax']:
        TVA = (dict_header['tax_rate'] * ht) / 100
        TTC = ht + TVA
        ctx.update({'tva': TVA, 'ttc': TTC, 'tax': dict_header['tax_rate']})
        # si le tax est prise en compte alors c'est le TTC qui doit être
        # convertie
        ht_en_lettre = cel(TTC)
    ctx.update({"ht_en_lettre": ht_en_lettre})
    # on teste le type
    if last_invoice.type == "Facture":
        type_ = "Pour acquit: "
    else:
        type_ = "Pour acceptation: "
    ctx.update({"type_": type_})
    return render_to_response('invoice_done.html', ctx)


@login_required
def show_invoice(request, *args, **kwargs):
    """ show a selected invoice in dashboard """
    user = request.user
    num = kwargs["id"] or 1
    # on recupere la facture a afficher
    invoice = Invoice.objects.get(id=num)
    #on recupere les items de la facture
    items_invoice = InvoiceItem.objects.filter(invoice=invoice.id)
    url = reverse('PDF_invoice_done', args=[invoice.id])
    try:
        dict_header = {'date': invoice.date, \
                      'number': invoice.number,\
                      'location': invoice.location,\
                      'subject': invoice.subject,\
                      'type': invoice.type,\
                      'client': invoice.client.name,\
                      'organization': invoice.organization,\
                      'tax': invoice.tax,\
                      'tax_rate': invoice.tax_rate,\
                      'logo': invoice.organization.image}
    except:
        blank_picture = Images()
        dict_header = {'date': invoice.date, \
                      'number': invoice.number,\
                      'location': invoice.location,\
                      'subject': invoice.subject,\
                      'type': invoice.type,\
                      'client': invoice.client.name,\
                      'organization': invoice.organization,\
                      'tax': invoice.tax,\
                      'tax_rate': invoice.tax_rate,\
                      'logo': blank_picture}
    c = {'invoice': invoice, 'dict_header': dict_header, 'url': url}
    lists, ht, comp = [], 0, 10
    for i in items_invoice:
        dic = {}
        dic['description'] = i.description
        dic['quantity'] = i.quantity
        dic['price'] = i.price
        dic['montant'] = i.price * i.quantity
        comp -= comp
        ht += dic['montant']
        lists.append(dic)
    nb = 10 - len(lists)

    while nb != 0:
        nb = nb - 1
        lists.append({})
    c.update({'lists': lists, 'ht': ht})
    ht_en_lettre = cel(ht)

    if dict_header['tax']:
        TVA = (dict_header['tax_rate'] * ht) / 100
        TTC = ht + TVA
        c.update({'tva': TVA, 'ttc': TTC, 'tax': dict_header['tax_rate']})
        ht_en_lettre = cel(TTC)

    c.update({"ht_en_lettre": ht_en_lettre})
    # on teste le type
    if invoice.type == "Facture":
        type_ = "Pour acquit: "
    else:
        type_ = "Pour acceptation: "
    c.update({"type_": type_})
    return render_to_response("invoice_done.html", c)


@login_required
def PDF_view(request, *args, **kwargs):
    """
        cette views est cree pour la generation du PDF
    """
    from datetime import datetime, timedelta
    from subprocess import Popen, PIPE
    from cStringIO import StringIO
    from reportlab.lib.pagesizes import landscape, A4, letter, portrait
    from reportlab. platypus import Image

    from super_code import controle_caratere

    user = request.user
    num = kwargs["id"] or 1
    # on recupere la facture a afficher
    invoice = Invoice.objects.get(id=num)
    #on recupere les items de la facture
    items_invoice = InvoiceItem.objects.filter(invoice=invoice.id)

    # Static source pdf to be overlayed
    PDF_SOURCE = 'media/css/images/fact1.pdf'
    DATE_FORMAT = u"%d/%m/%Y"

    DEFAULT_FONT_SIZE = 10
    FONT = 'Courier-Bold'
    # A simple function to return a leading 0 on any single digit int.

    def double_zero(value):
        try:
            return '%02d' % value
        except TypeError:
            return value

    # temporary file-like object in which to build the pdf containing
    # only the data numbers
    buffer = StringIO()

    # setup the empty canvas
    p = canvas.Canvas(buffer, pagesize=A4)
    p.setFont(FONT, DEFAULT_FONT_SIZE)

    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=facture.pdf'

    # Création de l'objet PDF, en utilisant l'objet de réponse comme "fichier"
    #on afffiche l'image de l'orgamisation
    try:
        p.drawInlineImage("media/%s" % invoice.organization.image, 60, 740,\
                                                                120, 60)
    except:
        pass
    p.drawString(370, 735, str(invoice.organization))
    # On trace Une ligne horizontale
    p.line(60, 730, 535, 730)

    p.drawString(59, 25, invoice.organization.address + "- tel : " +\
                         str(invoice.organization.address_extra) + " - " +\
                         str(invoice.organization.address_extra2))

    legal_infos, legal_infos1 = controle_caratere(invoice.organization.\
                                                    legal_infos, 55, 55)

    p.drawString(90, 14, legal_infos)
    p.drawString(90, 6, legal_infos1)
    p.drawString(60, 706, str(invoice.type) + "  N°: " + str(invoice.number))
    p.drawString(370, 706, "Date: " + str(invoice.date) + \
                              " à " + str(invoice.location))
    p.drawString(60, 690, "Doit: " + (invoice.client.name))

    if invoice.subject:
        p.drawString(60, 664, "Objet: " + str(invoice.subject))

    # On ecrit les invoiceitem
    x, y = 40, 600
    for i in items_invoice:
        p.drawString(x, y, str(i.quantity).rjust(10, ' '))
        p.drawString(x + 75, y, (i.description))
        p.drawString(x + 340, y, str(i.price).rjust(10, ' '))
        p.drawString(x + 435, y, str(i.price * i.quantity).rjust(10, ' '))
        y -= 20

    # on teste le type
    if invoice.type == "Facture":
        p.drawString(59, 95, "Pour acquit: ")
    else:
        p.drawString(59, 95, "Pour acceptation: ")

    p.drawString(435, 95, "Le fournisseur: ")
    #On calcul le montant total hors taxe et sa conversion en lettre
    ht = 0
    for i in items_invoice:
        montant = i.price * i.quantity
        ht += montant
    p.drawString(476, 204, str(ht).rjust(10, ' '))
    ht_en_lettre = cel(ht)
    # Calcul du TTC avec le TVA s'il existe
    if invoice.tax:
        TVA = (invoice.tax_rate * ht) / 100
        p.drawString(476, 183.5, str(TVA).rjust(10, ' '))
        TTC = ht + TVA
        p.drawString(476, 164, str(TTC).rjust(10, ' '))
        ht_en_lettre = cel(TTC)
        ht_en_lettre1, ht_en_lettre2 = controle_caratere(ht_en_lettre +\
                                                        " FCFA", 46, 40)
        p.drawString(263.8, 133, (ht_en_lettre1))
        p.drawString(53, 120, (ht_en_lettre2))

        p.drawString(415, 183.5, str(invoice.tax_rate))

    else:
        TTC = ht
        p.drawString(476, 164, str(TTC).rjust(10, ' '))
        ht_en_lettre1, ht_en_lettre2 = controle_caratere(ht_en_lettre + \
                                                        " FCFA", 46, 40)
        p.drawString(263.8, 133, (ht_en_lettre1))
        p.drawString(53, 120, (ht_en_lettre2))
        p.drawString(415, 183.5, str(0))
        p.drawString(476, 183.5, str(0).rjust(10, ' '))
    p.showPage()
    p.save()

    cmd = '/usr/bin/pdftk %s stamp - output -' % PDF_SOURCE

    proc = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    pdf, cmderr = proc.communicate(buffer.getvalue())
    buffer.close()
    response.write(pdf)
    return response
