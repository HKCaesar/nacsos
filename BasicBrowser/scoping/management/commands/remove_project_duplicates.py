from django.core.management.base import BaseCommand, CommandError
from scoping.models import *

from multiprocess import Pool
from functools import partial

import numpy as np
import re, nltk
from nltk.stem import SnowballStemmer

from utils.utils import *# flatten

class Command(BaseCommand):
    help = 'remove duplicates interactively'
    def add_arguments(self, parser):
        parser.add_argument('pid',type=int)
        parser.add_argument('qid',type=int)
        parser.add_argument('user_input', type=int)

    def handle(self, *args, **options):

        pid=options['pid']
        qid=options['qid']

        sdocs = Doc.objects.exclude(
            UT__UT__contains="WOS:",
            wosarticle__di__isnull=True
        )

        if qid:
            q = Query.objects.get(pk=qid)
            sdocs = sdocs.filter(query=q)

        p = Project.objects.get(pk=pid)

        for s in sdocs.iterator():
            docs = []
            py_docs = Doc.objects.exclude(id=s.id).filter(
                docproject__project=p,
                PY=s.PY
            )

            s1 = shingle(s.title)

            for d in py_docs:
                j = jaccard(s1,d.shingle())
                if j > 0.51:
                    docs.append(d)

            if len(docs)>0:
                if options['user_input'] == 0:
                    for d in docs:
                        for q in s.query.all():
                            d.query.add(q)
                    print("deleting {}".format(s.title))
                    s.delete()
                else:
                    print("{}: {} , {}, from queries {} \n \
                    \nmatches the following: ".format(
                        s.UT.UT,
                        s.title,
                        s.authors,
                        "; ".join([x.title for x in s.query.all()])
                    ))
                    i = 0
                    for d in docs:
                        print(
                            "{}: {} {}, {}, from queries {}".format(
                                i,
                                d.UT.UT,
                                d.title,
                                d.authors,
                                "; ".join([x.title for x in d.query.all()])
                            )
                        )
                        print('\n')
                        i+=1

                    print('##########\n')
                    print("Tell me what the original document is please. I'll transfer all information over to that one")
                    y = input('What\'s the document to keep? ')
                    if y=="o":
                        orig = s
                    else:
                        orig = docs[int(y)]

                    print('##########\n')
                    print("I'm going to give you a choice of which to delete now,\n\
    press \"o\" for the original, or a number for the numbered duplicate\n\
    to delete. Or enter \"s\" to skip")
                    print("You can combine choices in a list like [o,0,1,2]")
                    x = input('What do you want to delete?: ')

                    #try:
                    x = list(str(x))
                    for el in x:
                        try:
                            el = int(el)
                        except:
                            pass
                        if el=="o":
                            ut = s.UT.UT
                            del_doc = s
                            #s.delete()
                        elif isinstance(el, int):
                            ut = docs[el].UT.UT
                            del_doc = docs[el]
                        else:
                            print(repr(el))


                        for q in del_doc.query.all():
                            orig.query.add(q)

                        print("deleting doc {}".format(del_doc.UT.UT))
                        del_doc.delete()
    #                     except:
    #                         print("sorry I didn't manage to understand what you meant\n\
    # or didn't manage to act on it, I'm just goin to move on now...")
