
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Template, Context, RequestContext, loader
from tmv_app.models import *
from scoping.models import *
from django.db.models import Q, F, Sum, Count, FloatField, Case, When
from django.shortcuts import *
from django.forms import ModelForm
import random, sys, datetime
import urllib.request
from nltk.stem import SnowballStemmer
from django.http import JsonResponse
import json, csv
import decimal

# the following line will need to be updated to launch the browser on a web server
TEMPLATE_DIR = sys.path[0] + '/templates/'

opener = urllib.request.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]

global run_id

def find_run_id(request):
    try:
        run_id = request['run_id']
    except:
        settings = Settings.objects.all().first()
        run_id = settings.run_id
        try:
            request['run_id'] = run_id
        except:
            pass
    return(int(run_id))

def get_year_filter(request):
    try:
        y1 = request.session['y1']
        y2 = request.session['y2']
    except:
        y1 = 1990
        y2 = 2016
        request.session['y1'] = y1
        request.session['y2'] = y2

    return([y1,y2])

def show_toolbar(request):
    return True
DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK" : show_toolbar,
}

def author_detail(request, author_name):
    run_id = find_run_id(request.session)
    response = author_name
    documents = Doc.objects.filter(docauthinst__AU=author_name)

    dt_threshold = Settings.objects.get(id=1).doc_topic_score_threshold

    topics = DocTopic.objects.filter(
        doc__docauthinst__AU=author_name,
        scaled_score__gt=dt_threshold/80,
        run_id=run_id
    )

    topics = topics.annotate(total=(Sum('scaled_score')))

    topics = topics.values('topic','topic__title').annotate(
        tprop=Sum('scaled_score')
    ).order_by('-tprop')

    pie_array = []
    for t in topics:
        pie_array.append([t['tprop'], '/topic/' + str(t['topic']), 'topic_' + str(t['topic'])])

    author_template = loader.get_template('tmv_app/author.html')

    author_page_context = Context({'author': author_name, 'docs': documents, 'topics': topics, 'pie_array': pie_array})

    return HttpResponse(author_template.render(author_page_context))

###########################################################################
## Institution view
def institution_detail(request, run_id, institution_name):
    documents = Doc.objects.filter(
        docauthinst__institution__icontains=institution_name
    ).distinct('UT')

    topics = {}
    topics = Topic.objects.all()
    topics = []

    topics = DocTopic.objects.filter(
        doc__docauthinst__institution__icontains=institution_name,
        scaled_score__gt=0.00002,run_id=run_id
    )

    topics = topics.annotate(total=(Sum('scaled_score')))

    topics = topics.values('topic','topic__title').annotate(
        tprop=Sum('scaled_score')
    ).order_by('-tprop')

    pie_array = []
    for t in topics:
        pie_array.append([t['tprop'], '/topic/' + str(t['topic']), 'topic_' + str(t['topic'])])

    institution_template = loader.get_template('tmv_app/institution.html')

    institution_page_context = Context({
        'institution': institution_name,
        'docs': documents,
        'topics': topics,
        'pie_array': pie_array
    })

    return HttpResponse(institution_template.render(institution_page_context))

def index(request):
    template = loader.get_template('tmv_app/network.html')
    run_id = find_run_id(request.session)

    nodes = json.dumps(list(Topic.objects.filter(run_id=run_id).values('id','title','score')),indent=4,sort_keys=True)
    links = TopicCorr.objects.filter(run_id=run_id,ar=-1).filter(score__gt=0.05,score__lt=1).annotate(
        source=F('topic'),
        target=F('topiccorr')
    )
    links = json.dumps(list(links.values('source','target','score')),indent=4,sort_keys=True)
    context = {
        "nodes":nodes,
        "links":links
    }

    return HttpResponse(template.render(context, request))

def network(request,run_id):
    ar = -1
    template = loader.get_template('tmv_app/network.html')
    nodes = Topic.objects.filter(run_id=run_id)
    nodes = nodes.annotate(
                arscore = F('score')
            )
    nodes = nodes.values('id','title','arscore','score')
    nodes = json.dumps(list(nodes),indent=4,sort_keys=True)
    links = TopicCorr.objects.filter(run_id=run_id).filter(score__gt=0.05,score__lt=1,ar=ar).annotate(
        source=F('topic'),
        target=F('topiccorr')
    )
    links = json.dumps(list(links.values('source','target','score')),indent=4,sort_keys=True)
    context = {
        "nodes":nodes,
        "links":links,
        "run_id":run_id,
        "stat": RunStats.objects.get(pk=run_id)
    }

    return HttpResponse(template.render(context, request))

def return_corrs(request):
    cor = float(request.GET.get('cor',None))
    run_id = int(request.GET.get('run_id',None))
    ar = int(request.GET.get('ar',None))
    nodes = Topic.objects.filter(run_id=run_id)
    if ar > -1:
        a = AR.objects.get(ar=ar)
        nodes = Topic.objects.filter(run_id=run_id)
        if TopicARScores.objects.filter(topic=nodes[0],ar=a).count() == 0:
            nodes = nodes.annotate(
                arscore = Sum(
                    Case(When(
                        doctopic__doc__PY__gte=a.start,
                        doctopic__doc__PY__lte=a.end,
                        then=F('doctopic__score')),
                        #default=0,
                        output_field=models.FloatField()
                    )
                )
            )
            for node in nodes:
                tar = TopicARScores(
                    topic=node,
                    ar=a,
                    score=node.arscore
                )
                tar.save()
        else:
            nodes = nodes.annotate(
                arscore = Sum(
                    Case(When(
                        topicarscores__ar=a,
                        #doctopic__doc__PY__lte=a.end,
                        then=F('topicarscores__score')),
                        #default=0,
                        output_field=models.FloatField()
                    )
                )
            )
            for node in nodes:
                node.arscore = TopicARScores.objects.get(topic=node,ar=a).score
    else:
        nodes = nodes.annotate(
            arscore = F('score')
        )
    nodes = list(nodes.values('id','title','score','arscore'))
    links = TopicCorr.objects.filter(run_id=run_id).filter(score__gt=cor,score__lt=1,ar=ar).annotate(
        source=F('topic'),
        target=F('topiccorr')
    )
    links = list(links.values('source','target','score'))
    context = {
        "nodes":nodes,
        "links":links
    }
    return HttpResponse(json.dumps(context,sort_keys=True))

#######################################################################
## DynamicTopic View
def dynamic_topic_detail(request,topic_id):
    template = loader.get_template('tmv_app/dynamic_topic.html')

    topic = DynamicTopic.objects.get(pk=topic_id)
    run_id = topic.run_id.run_id

    topicterms = Term.objects.filter(
        dynamictopicterm__topic=topic, run_id=run_id,
        dynamictopicterm__score__gt=0.00001
    ).order_by('-dynamictopicterm__score')[:50]

    wtopics = Topic.objects.filter(
        run_id=run_id,primary_dtopic=topic
    ).order_by('year')

    for t in wtopics:
        if t.top_words is not None:
            t.tts = t.top_words
        else:
            t.tts = Term.objects.filter(
                topicterm__topic=t, run_id=run_id,
                topicterm__score__gt=0.00001
            ).order_by('-topicterm__score')[:10]
        score = TopicDTopic.objects.get(
            topic=t,dynamictopic=topic
        ).score
        t.score = round(score,2)

    docs = DocTopic.objects.filter(
        #topic__primary_dtopic=topic,
        run_id=run_id,
        topic__topicdtopic__dynamictopic=topic
    )

    docs = docs.annotate(
        topic_combination = F('score') * F('topic__topicdtopic__score')
    ).order_by('-topic_combination')[:50].values(
        'doc__pk','doc__PY','doc__title','topic_combination'
    )

    dtopics = Topic.objects.filter(
        run_id=run_id,
        year__lt=2200
    ).order_by('year').annotate(
        dscore = Sum(
            Case(
                When(topicdtopic__dynamictopic=topic,
                    then=F('topicdtopic__score')),
                default=0,
                output_field=models.FloatField()
            )
        )
    )

    ysums = dtopics.values('year').annotate(
        sum = Sum('score'),
    )


    context = RequestContext(request, {
        'run_id': run_id,
        'topic': topic,
        'topicterms': topicterms,
        'wtopics': wtopics,
        'wtvs': list(dtopics.values('title','score','year','dscore')),
        'ysums': list(ysums.values('year','sum')),
        'docs': docs
    })
    return HttpResponse(template.render(context))

def dtopic_detail(request,topic_id):
    template = loader.get_template('tmv_app/dtopic.html')

    topic = Topic.objects.get(pk=topic_id)

    tterms = []
    tts = TopicTerm.objects.filter(topic=topic)
    for py in tts.distinct('PY') \
        .order_by('PY').values_list('PY',flat=True):
        ytts = tts.filter(PY=py).order_by('-score')[:10]
        tterms.append(ytts)

    docs = Doc.objects.filter(doctopic__topic=topic) \
        .order_by('-doctopic__score')[:50]

    context = Context({
        "topic":topic,
        "tterms": tterms,
        "docs": docs
    })

    return HttpResponse(template.render(context))

###########################################################################
## Topic View
def topic_detail(request, topic_id):

    template = loader.get_template('tmv_app/topic.html')

    try:
        topic = Topic.objects.get(pk=topic_id)
    except:
        return(topic_detail_hlda(request, topic_id))

    if topic.run_id.method=="BD":
        return(dtopic_detail(request,topic_id))
    run_id = topic.run_id.pk
    stat = RunStats.objects.get(run_id=run_id)

    topic_template = loader.get_template('tmv_app/topic.html')

    topic = Topic.objects.get(pk=topic_id,run_id=run_id)

    topicterms = Term.objects.filter(
        topicterm__topic=topic, run_id=run_id,
        topicterm__score__gt=0.00001
    ).order_by('-topicterm__score')[:50]

    if Settings.objects.first().doc_topic_scaled_score==True:
        doctopics = Doc.objects.filter(
            doctopic__topic=topic,doctopic__run_id=run_id
        ).order_by('-doctopic__scaled_score')[:50]
    else:
        doctopics = Doc.objects.filter(
            doctopic__topic=topic,doctopic__run_id=run_id
        ).order_by('-doctopic__score')[:50]

    doctopics = doctopics.values('PY','title','pk','doctopic__score')
    terms = []
    term_bar = []
    remainder = 1
    remainder_titles = ''

    for tt in topicterms:
        term = Term.objects.get(pk=tt.pk)
        score = tt.topicterm_set.all()[0].score

        terms.append(term)
        if score >= .00001:
            term_bar.append((True, term, score * 100))
            remainder -= score
        else:
            if remainder_titles == '':
                remainder_titles += term.title
            else:
                remainder_titles += ', ' + term.title
    term_bar.append((False, remainder_titles, remainder*100))

    yts = TopicYear.objects.filter(run_id=run_id)

    ytarray = list(yts.values('PY','count','score','topic_id','topic__title'))

    corrtops = TopicCorr.objects.filter(topic=topic_id,score__lt=1,ar=-1).order_by('-score')[:10]
    dtops = TopicDTopic.objects.filter(
        topic=topic_id
    ).order_by('-score')[:10]

    topic_page_context = Context({
        'topic': topic,
        'terms': terms,
        'term_bar': term_bar,
        'docs': doctopics,
        'yts': ytarray,
        'corrtops': corrtops,
        'dtops': dtops,
        'run_id': run_id
        })

    return HttpResponse(topic_template.render(topic_page_context))

def get_topic_docs(request,topic_id):

    template = loader.get_template('tmv_app/topic_docs.html')
    topic = Topic.objects.get(pk=topic_id)
    run_id = topic.run_id.pk

    stat = RunStats.objects.get(run_id=run_id)

    dt_threshold = Settings.objects.get(id=1).doc_topic_score_threshold
    dt_thresh_scaled = Settings.objects.get(id=1).doc_topic_scaled_score
    if stat.method=="BD":
        dt_threshold=dt_threshold*100

    svalue = request.GET.get('sort',None)
    sortcol = svalue.replace('-','')



    doctopics = Doc.objects.filter(
        doctopic__topic=topic,doctopic__run_id=run_id,
        doctopic__score__gt=dt_threshold
    )
    if sortcol != "doctopic__score":
        doctopics = doctopics.filter(**{sortcol+'__isnull': False})
    doctopics = doctopics.order_by(svalue)[:50]


    doctopics = doctopics.annotate(
        svalue=F(sortcol)
    )
    doctopics = doctopics.values('PY','title','pk','doctopic__score','svalue')

    d = decimal.Decimal(doctopics[0]['svalue'])
    float = abs(d.as_tuple().exponent)
    if float > 3:
        float=4

    #x = y
    context = Context({
        "docs": doctopics,
        "svalue": sortcol,
        "topic": topic,
        "float": float
    })

    return HttpResponse(template.render(context))

def multi_topic(request):

    template = loader.get_template('tmv_app/multi_topic_docs.html')
    topics = request.GET.getlist('topics[]',None)

    doctopics = DocTopic.objects.filter(
        topic__in=topics,
        score__gt=0
    )
    x = doctopics.values()[:5]

    combine = doctopics.values('doc').annotate(
        topic_combination = Sum('score'),
        count = Count('score')
    ).filter(count__gte=len(topics))

    annotation = {}

    combine2 = combine.values('doc')
    for t in topics:
        annotation[t] = Sum(
            Case(When(topic=t,then=F('score')),
                #default=0,
                output_field=models.FloatField()
            )
        )

    combine2 = combine2.annotate(**annotation)
    combine2 = combine2.annotate(topic_combination=F(topics[0]))

    for i in range(1,len(topics)):
        combine2 = combine2.annotate(
            topic_combination=F('topic_combination')*F(topics[i])
        )

    y = combine2.order_by('-topic_combination')[:50]
    y= y.values('doc__pk','doc__PY','doc__title','topic_combination')

    context = Context({
        'docs' : y,
        'topic': Topic.objects.get(pk=topics[0])
    })

    return HttpResponse(template.render(context))

###########################################################################
## Topic View for HLDA
def topic_detail_hlda(request, topic_id):
    #update_year_topic_scores(request.session)
    response = ''
    run_id = find_run_id(request.session)

    topic_template = loader.get_template('tmv_app/topic.html')

    topic = HTopic.objects.get(topic=topic_id,run_id=run_id)
    topicterms = Term.objects.filter(htopicterm__topic=topic.topic, run_id=run_id).order_by('-htopicterm__count')[:10]
    doctopics = Doc.objects.filter(hdoctopic__topic=topic.topic,hdoctopic__run_id=run_id)

    terms = []
    term_bar = []
    remainder = 1
    remainder_titles = ''

    for tt in topicterms:
        term = Term.objects.get(term=tt.term)

        terms.append(term)

#            term_bar.append((True, term, score * 100))
#            remainder -= score
#        else:
#            if remainder_titles == '':
#                remainder_titles += term.title
#            else:
#                remainder_titles += ', ' + term.title
#    term_bar.append((False, remainder_titles, remainder*100))

    update_year_topic_scores(request.session)

    yts = HTopicYear.objects.filter(run_id=run_id)

    ytarray = list(yts.values('PY','count','score','topic_id','topic__title'))
    #ytarray = []

    corrtops = TopicCorr.objects.filter(topic=topic_id).order_by('-score')[:10]

    ctarray = []

    for ct in corrtops:
        top = Topic.objects.get(topic=ct.topiccorr)
        if ct.score < 1:
            score = round(ct.score,2)
            ctarray.append({"topic": top.topic,"title":top.title,"score":score})

    topic_page_context = Context({'topic': topic, 'terms': terms, 'term_bar': term_bar, 'docs': doctopics, 'yts': ytarray, 'corrtops': ctarray})

    return HttpResponse(topic_template.render(topic_page_context))

##############################################################

def term_detail(request, term_id):
    update_topic_titles(request.session)
    run_id = find_run_id(request.session)
    response = ''

    term_template = loader.get_template('tmv_app/term.html')

    term = Term.objects.get(pk=term_id,run_id=run_id)
    topics = TopicTerm.objects.filter(term=term_id,run_id=run_id).order_by('-score')
    if len(topics) > 0:
        topic_tuples = []
        max_score = topics[0].score
        for topic in topics:
            topic_tuples.append((topic.topic, topic.score, topic.score/max_score*100))

    term_page_context = Context({'term': term, 'topic_tuples': topic_tuples})

    return HttpResponse(term_template.render(term_page_context))

#######################################################################
## Doc view

def doc_detail(request, doc_id, run_id):

    snowball_stemmer = SnowballStemmer("english")


    stat = RunStats.objects.get(run_id=run_id)
    if stat.get_method_display() == 'hlda':
        return(doc_detail_hlda(request, doc_id))
    update_topic_titles(int(run_id))
    response = ''
    template = loader.get_template('tmv_app/doc.html')

    doc = Doc.objects.get(UT=doc_id)

    doctopics = DocTopic.objects.filter(doc=doc_id,run_id=run_id).order_by('-score')

    doc_authors = DocAuthInst.objects.filter(doc=doc).distinct('AU')

    #doc_institutions = DocInstitutions.objects.filter(doc__UT=doc_id)
    #for di in doc_institutions:
    #    di.institution = di.institution.split(',')[0]

    topics = []
    pie_array = []
    dt_threshold = Settings.objects.get(id=1).doc_topic_score_threshold
    dt_thresh_scaled = Settings.objects.get(id=1).doc_topic_scaled_score
    if stat.method=="BD":
        dt_threshold=dt_threshold*100
    topicwords = {}
    ntopic = 0
    for dt in doctopics:
#        if ((not dt_thresh_scaled and dt.score >= dt_threshold) or (dt_thresh_scaled and dt.scaled_score*100 >= dt_threshold)):
        if ((dt_thresh_scaled and dt.scaled_score*80 >= dt_threshold) or
            (not dt_thresh_scaled and dt.score >= dt_threshold)):
            topic = Topic.objects.get(pk=dt.topic_id)
            ntopic+=1
            topic.ntopic = "t"+str(ntopic)
            topics.append(topic)
            if stat.method=="BD":
                terms=Term.objects.filter(
                    topicterm__topic=topic.pk,
                    topicterm__PY=doc.PY
                ).order_by('-topicterm__score')[:10]
            else:
                terms = Term.objects.filter(topicterm__topic=topic.pk).order_by('-topicterm__score')[:10]

            topicwords[ntopic] = []
            for tt in terms:
                topicwords[ntopic].append(tt.title)
            if not dt_thresh_scaled:
                pie_array.append([dt.score, '/tmv_app/topic/' + str(topic.pk), 'topic_' + str(topic.pk)])
            else:
                pie_array.append([dt.scaled_score, '/tmv_app/topic/' + str(topic.pk), 'topic_' + str(topic.pk)])


    words = []
    for word in doc.content.split():
        wt = ""
        for t in range(1,ntopic+1):
            if snowball_stemmer.stem(word) in topicwords[t] or word in topicwords[t]:
            #if word in topicwords[t]:
                wt = t
        words.append({'title': word, 'topic':"t"+str(wt)})

    context = RequestContext(request, {
        'doc': doc,
        'topics': topics,
        'pie_array': pie_array,
        'doc_authors': doc_authors,
        'words': words,
        'run_id': run_id
    })


    return HttpResponse(template.render(context))

def print_table(request,run_id):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="topic_table.csv"'

    topics = Topic.objects.filter(run_id=run_id).order_by('-score')
    tsum = topics.aggregate(
        tsum=Sum('score')
    )

    for t in topics:
        termlist= list(Term.objects.filter(
            topicterm__topic=t, run_id=run_id,
            topicterm__score__gt=0.00001
        ).order_by('-topicterm__score')[:5].values_list('title',flat=True))
        t.terms = "; ".join(termlist)
        t.mtd = t.score/tsum['tsum']*100

    writer = csv.writer(response)

    writer.writerow(["Topic ID","Topic Name","Stemmed Keywords","Marginal Topic Distribution"])

    for t in topics:
        row = [t.pk,"",t.terms,t.mtd]
        writer.writerow(row)

    return response

############################################################################
## for HLDA
def doc_detail_hlda(request, doc_id):

    snowball_stemmer = SnowballStemmer("english")

    run_id = find_run_id(request.session)

    update_topic_titles(request.session)
    response = ''
    doc_template = loader.get_template('tmv_app/doc.html')

    doc = Doc.objects.get(UT=doc_id)

    doctopics = HDocTopic.objects.filter(doc=doc_id,run_id=run_id).order_by('level')

    doc_authors = DocAuthors.objects.filter(doc__UT=doc_id).distinct('author')

    doc_institutions = DocInstitutions.objects.filter(doc__UT=doc_id)
    for di in doc_institutions:
        di.institution = di.institution.split(',')[0]

    topics = []
    pie_array = []

    topicwords = {}
    ntopic = 0
    for dt in doctopics:
        topic = HTopic.objects.get(topic=dt.topic_id)
        ntopic+=1
        topic.ntopic = "t"+str(ntopic)
        topics.append(topic)
        terms = Term.objects.filter(htopicterm__topic=topic.topic).order_by('-htopicterm__count')[:10]

        topicwords[ntopic] = []
        for tt in terms:
            topicwords[ntopic].append(tt.title)
        pie_array.append([dt.score, '/topic/' + str(topic.topic), 'topic_' + str(topic.topic)])


    words = []
    for word in doc.content.split():
        wt = ""
        for t in range(1,ntopic+1):
            if snowball_stemmer.stem(word) in topicwords[t]:
                wt = t
        words.append({'title': word, 'topic':"t"+str(wt)})

    doc_page_context = Context({'doc': doc, 'topics': topics, 'pie_array': pie_array,'doc_authors': doc_authors, 'doc_institutions': doc_institutions , 'words': words })

    return HttpResponse(doc_template.render(doc_page_context))


def topic_list_detail(request):
    run_id = find_run_id(request.session)
    update_topic_titles()
    response = ''

    template_file = open(TEMPLATE_DIR + 'topic_list.html', 'r')
    list_template = Template(template_file.read())

    topics = Topic.objects.all()

    terms = []
    for t in topics:
        topicterms = TopicTerm.objects.filter(topic=t.topic).order_by('-score')[:5]
        temp =[]
        term_count = 5
        for tt in topicterms:
            temp.append(Term.objects.get(term=tt.term))
            term_count -= 1
        for i in range(term_count):
            temp.append(None)
        terms.append(temp)

    div_topics = []
    div_terms = []
    rows = []
    n = 3
    for i in xrange(0, len(topics), n):
        temp = []
        for j in range(5):
            K = min(len(topics), i+n)
            t = [terms[k][j] for k in range(i,K,1)]
            while len(t) < n:
                t.append(None)
            temp.append(t)
        tops = topics[i:i+n]
        while len(tops) < n:
            tops.append(None)
        rows.append((tops, temp))

    list_page_context = Context({'rows': rows})

    return HttpResponse(list_template.render(list_page_context))

#################################################################
### Main page!
def topic_presence_detail(request,run_id):
    stat = RunStats.objects.get(run_id=run_id)
    if stat.get_method_display() == 'hlda':
        return(topic_presence_hlda(request))

    if stat.method == "DT":
        update_dtopics(run_id)
    if stat.method == "BD":
        update_bdtopics(run_id)


    run_id = int(run_id)

    update_topic_titles(run_id)
    update_topic_scores(run_id)


    response = ''

    get_year_filter(request)

    presence_template = loader.get_template('tmv_app/topic_presence.html')
    print(stat.method)
    if stat.method=="DT":
        topics = DynamicTopic.objects.filter(run_id=run_id).order_by('-score')
    else:
        topics = Topic.objects.filter(run_id=run_id).order_by('-score')
    max_score = topics[0].score

    topic_tuples = []
    for topic in topics:
        s = topic.score
        topic_tuples.append((topic, topic.score, topic.score/max_score*100))

    presence_page_context = Context({
        'run_id': run_id, 'topic_tuples': topic_tuples,
        'stat': stat
    })

    return HttpResponse(presence_template.render(presence_page_context))

##################################################################
## Alt Main page for hlda

def topic_presence_hlda(request):
    run_id = find_run_id(request.session)
    update_topic_titles_hlda(request.session)
    update_topic_scores(request.session)
    response = ''

    get_year_filter(request)

    presence_template = loader.get_template('tmv_app/topic_presence_hlda.html')

    topics = HTopic.objects.filter(run_id=run_id).order_by('-n_docs')
    max_score = topics[0].n_docs

    topic_tuples = []

    ttree = "{"

    for topic in topics:
        topic_tuples.append((topic, topic.n_docs, topic.n_docs/max_score*100))

    topics = topics.values()

    root = topics[0]
    root['children'] = []
    root['parent_id'] = "null"

    for topic in topics:
        if topic['parent_id']==root['topic']:
            topic['children'] = []
            for child in topics:
                if child['parent_id']==topic['topic']:
                    child['children'] = []
                    for grandchild in topics:
                        if grandchild['parent_id']==child['topic']:
                            child['children'].append(grandchild)
                    topic['children'].append(child)
            root['children'].append(topic)

    presence_page_context = Context({'topic_tuples': topic_tuples,'topic_tree': root})

    return HttpResponse(presence_template.render(presence_page_context))

def get_docs(request):
    topic = request.GET.get('topic',None)
    t = HTopic.objects.get(topic=topic)
    topic_box_template = loader.get_template('tmv_app/topic_box.html')
    docs = Doc.objects.filter(hdoctopic__topic=topic).order_by('hdoctopic__score')[:5].values()
    data = {
        "bla": "bla"
    }
    topic_box_context = Context({'docs':docs, 'topic':t})
    return HttpResponse(topic_box_template.render(topic_box_context))

def stats(request,run_id):

    template = loader.get_template('tmv_app/stats.html')

    stats = RunStats.objects.get(run_id=run_id)

    if stats.get_method_display() == 'hlda':
        docs_seen = HDocTopic.objects.filter(run_id=run_id).values('doc_id').order_by().distinct().count()
    else:
        docs_seen = DocTopic.objects.filter(run_id=run_id).values('doc_id').order_by().distinct().count()

    stats.docs_seen = docs_seen
    stats.num_docs = stats.query.doc_set.count()

    stats.save()

    context = Context({
        'stats': stats,
        'num_topics': Topic.objects.filter(run_id=run_id).count(),
        'num_terms': Term.objects.filter(run_id=run_id).count(),
    })

    return HttpResponse(template.render(context))

def runs(request):

    template = loader.get_template('tmv_app/runs.html')
    stats = RunStats.objects.all().order_by('-start')

    stats = stats.annotate(
        topics = models.Count('topic')#,
        #terms = models.Count('term')
    )
    for s in stats:
        if s.term_count is None:
            s.term_count = Term.objects.filter(run_id=s.run_id).count()
            s.save()

    context = Context({'stats':stats})

    return HttpResponse(template.render(context, request))

class SettingsForm(ModelForm):
    class Meta:
        model = Settings
        fields = '__all__'

def queries(request):

    return HttpResponse("bla")

def settings(request):
    run_id = find_run_id(request)

    settings_template = loader.get_template('tmv_app/settings.html')

    settings_page_context = Context({'settings': Settings.objects.get(id=1)})

    return HttpResponse(settings_template.render(settings_page_context,request))
    #return render_to_response('settings.html', settings_page_context, context_instance=RequestContext(request))

def apply_settings(request):
    settings = Settings.objects.get(id=1)
    form = SettingsForm(request.POST, instance=settings)
    #TODO: add in checks for threshold (make sure it's a float)
    settings.doc_topic_score_threshold = float(request.POST['doc_topic_score_threshold'])
    try:
        scaled = request.POST['doc_topic_scaled_score']
        scaled = True
    except:
        scaled = False
    settings.doc_topic_scaled_score = scaled
    settings.save()

    return HttpResponseRedirect(reverse('tmv_app:topics'))

from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render

def update_run(request, run_id):
    try:
        stat = RunStats.objects.get(run_id=run_id)
        stat.notes = request.POST['notes']
        stat.save()
    except:
        pass

    return HttpResponseRedirect(reverse('tmv_app:runs'))

def apply_run_filter(request,new_run_id):
#    settings = Settings.objects.get(id=1)
#    settings.run_id = new_run_id
#    settings.save()
    request.session['run_id'] = new_run_id

    return HttpResponseRedirect('/tmv_app/runs')

def delete_run(request,new_run_id):
    stat = RunStats.objects.get(run_id=new_run_id)
    stat.delete()
    topics = Topic.objects.filter(run_id_id=new_run_id)
    topics.delete()
    dt = DocTopic.objects.filter(run_id=new_run_id)
    dt.delete()
    tt = TopicTerm.objects.filter(run_id=new_run_id)
    tt.delete()
    ht = HTopic.objects.filter(run_id=new_run_id)
    ht.delete()
    hd = HDocTopic.objects.filter(run_id=new_run_id)
    DynamicTopic.objects.filter(run_id=new_run_id).delete()


    return HttpResponseRedirect('/tmv_app/runs')



def update_topic_titles(session):
    if isinstance(session, int):
        run_id=session
    else:
        run_id = find_run_id(session)

    stats = RunStats.objects.get(run_id=run_id)
    if not stats.topic_titles_current:
    #if "a" in "ab":
        for topic in Topic.objects.filter(run_id=run_id):
            #topicterms = TopicTerm.objects.filter(topic=topic.topic).order_by('-score')[:3]
            topicterms = Term.objects.filter(topicterm__topic=topic).order_by('-topicterm__score')[:10]
            new_topic_title = '{'
            for tt in topicterms[:3]:
                new_topic_title +=tt.title
                new_topic_title +=', '
            new_topic_title = new_topic_title[:-2]
            new_topic_title+='}'

            topic.top_words = [x.title.lower() for x in topicterms]

            topic.title = new_topic_title
            topic.save()
        stats.topic_titles_current = True
        stats.save()

def update_bdtopics(run_id):
    stats = RunStats.objects.get(pk=run_id)
    if "a"=="a":
    #if not stats.topic_titles_current:
        topics = Topic.objects.filter(run_id=run_id)
        for topic in topics:
            tts = TopicTerm.objects.filter(topic=topic)
            at = tts.values('term').annotate(
                mean = models.Avg('score')
            ).order_by('-mean')[:3]
            new_topic_title = '{'
            for tt in at:
                term = Term.objects.get(pk=tt['term'])
                new_topic_title += term.title
                new_topic_title +=', '
            new_topic_title = new_topic_title[:-2]
            new_topic_title+='}'
            topic.title = new_topic_title
            topic.save()

def update_dtopics(run_id):
    stats = RunStats.objects.get(pk=run_id)
    #if "a" == "b":
    #if not stats.topic_titles_current:
    if "a" in "ab":
        #print("UPDATING")
        for topic in DynamicTopic.objects.filter(run_id=run_id):
            topicterms = Term.objects.filter(
                dynamictopicterm__topic=topic
            ).order_by('-dynamictopicterm__score')[:10]
            new_topic_title = '{'
            for tt in topicterms[:3]:
                new_topic_title +=tt.title
                new_topic_title +=', '
            new_topic_title = new_topic_title[:-2]
            new_topic_title+='}'
            topic.title = new_topic_title
            topic.score = 0
            score = DocTopic.objects.filter(
                run_id=run_id,topic__primary_dtopic=topic
            ).aggregate(
                t=Sum('score')
            )['t']
            if score is not None:
                topic.score = score
            topic.save()
        #stats.topic_titles_current = True
        #stats.save()

    return

def update_topic_titles_hlda(session):
    if isinstance(session, int):
        run_id=session
    else:
        run_id = find_run_id(session)

    stats = RunStats.objects.get(run_id=run_id)
    if not stats.topic_titles_current:
    #if "a" in "ab":
        for topic in HTopic.objects.filter(run_id=run_id):
            #topicterms = TopicTerm.objects.filter(topic=topic.topic).order_by('-score')[:3]
            topicterms = Term.objects.filter(htopicterm__topic=topic.topic).order_by('-htopicterm__count')[:3]
            new_topic_title = '{'
            for tt in topicterms:
                new_topic_title +=tt.title
                new_topic_title +=', '
            new_topic_title = new_topic_title[:-2]
            new_topic_title+='}'

            topic.title = new_topic_title
            topic.save()
        stats.topic_titles_current = True
        stats.save()


def update_topic_scores(session):
    if isinstance(session, int):
        run_id=session
    else:
        run_id = find_run_id(session)
    stats = RunStats.objects.get(run_id=run_id)
    #if "a" in "ab":
    if not stats.topic_scores_current:

        topics = Topic.objects.filter(run_id=stats)
        for t in topics:
            t.score=0
            t.save()

        topics = DocTopic.objects.filter(run_id=run_id).values('topic').annotate(
            total=Sum('score')
        )
        for tscore in topics:
            topic = Topic.objects.get(pk=tscore['topic'])
            topic.score = tscore['total']
            topic.save()



        stats.topic_scores_current = True
        stats.save()

def update_year_topic_scores(session):
    if isinstance(session, int):
        run_id=session
    else:
        run_id = find_run_id(session)
    stats = RunStats.objects.get(run_id=run_id)
    #if "a" in "a":
    if not stats.topic_year_scores_current:
        if stats.get_method_display() == 'hlda':
            yts = HDocTopic.objects.filter(doc__PY__gt=1989,run_id=run_id)

            yts = yts.values('doc__PY').annotate(
                yeartotal=Count('doc')
            )

            ytts = yts.values().values('topic','topic__title','doc__PY').annotate(
                score=Count('doc')
            )
            HTopicYear.objects.filter(run_id=run_id).delete()
            for ytt in ytts:
                yttyear = ytt['doc__PY']
                topic = HTopic.objects.get(topic=ytt['topic'])
                for yt in yts:
                    ytyear = yt['doc__PY']
                    if yttyear==ytyear:
                        yeartotal = yt['yeartotal']
                try:
                    topicyear = HTopicYear.objects.get(topic=topic,PY=yttyear, run_id=run_id)
                except:
                    topicyear = HTopicYear(topic=topic,PY=yttyear,run_id=run_id)
                topicyear.score = ytt['score']
                topicyear.count = yeartotal
                topicyear.save()
        else:
            yts = DocTopic.objects.filter(doc__PY__gt=1989,run_id=run_id)

            yts = yts.values('doc__PY').annotate(
                yeartotal=Sum('scaled_score')
            )

            ytts = yts.values().values('topic','topic__title','doc__PY').annotate(
                score=Sum('scaled_score')
            )
            TopicYear.objects.filter(run_id=run_id).delete()
            for ytt in ytts:
                yttyear = ytt['doc__PY']
                topic = Topic.objects.get(pk=ytt['topic'])
                for yt in yts:
                    ytyear = yt['doc__PY']
                    if yttyear==ytyear:
                        yeartotal = yt['yeartotal']
                try:
                    topicyear = TopicYear.objects.get(topic=topic,PY=yttyear, run_id=run_id)
                except:
                    topicyear = TopicYear(topic=topic,PY=yttyear,run_id=run_id)
                topicyear.score = ytt['score']
                topicyear.count = yeartotal
                topicyear.save()



        stats.topic_year_scores_current = True
        stats.save()


def topic_random(request):
    return HttpResponseRedirect('/tmv_app/topic/' + str(random.randint(1, Topic.objects.count())))

def doc_random(request,run_id):
    doc = random_doc(RunStats.objects.get(pk=run_id).query)
    return HttpResponseRedirect('/tmv_app/doc/' +  doc.UT + '/' + run_id)

def term_random(request):
    return HttpResponseRedirect('/tmv_app/term/' + str(random.randint(1, Term.objects.count())))
