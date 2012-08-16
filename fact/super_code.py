#!/usr/bin/env python
# -*- coding: utf-8 -*-
#


def controle_caratere(lettre, nb_controle, nb_limite):
    """
        cette fonction decoupe une chaine de caratere en fonction
        du nombre de caratere donnée et conduit le reste à la ligne
    """
    lettre = lettre
    if len(lettre) <= nb_controle:
        ch = lettre
        ch2 = ""
        return ch, ch2
    else:
        ch = ch2 = ""
        for n in lettre.split(" "):
            if len(ch) <= nb_limite:
                ch = ch + " " + n
            else:
                ch2 = ch2 + " " + n
        return ch, ch2
