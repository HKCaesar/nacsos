from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from nltk import ngrams

# Create your models here.

class SnowballingSession(models.Model):

    INPROGRESS = 0
    COMPLETED  = 1

    Status = (
        (INPROGRESS, 'In progress'),
        (COMPLETED,  'Completed'),
    )


    name           = models.TextField(null=True, unique=True, verbose_name="SB Name")
    initial_pearls = models.TextField(null=True,              verbose_name="SB Initial Pearls")
    date           = models.DateTimeField(                    verbose_name="SB Date")
#    completed      = models.BooleanField(verbose_name="Is SB Completed")
    status         = models.IntegerField(
                         choices      = Status,
                         default      = 0,
                         db_index     = True,
                         verbose_name = "SB Status")
    users          = models.ManyToManyField(User)
    database       = models.CharField(max_length=6,null=True, verbose_name="Query database")
    technology     = models.ForeignKey('Technology', null=True)

    def __str__(self):
      return self.name

class Query(models.Model):
    type        = models.TextField(null=True, verbose_name="Query Type", default="default")
    title       = models.TextField(null=True, verbose_name="Query Title")
    text        = models.TextField(null=True, verbose_name="Query Text")
    database    = models.CharField(max_length=6,null=True, verbose_name="Query database")
    date        = models.DateTimeField(verbose_name="Query Date")
    r_count     = models.IntegerField(null=True, verbose_name="Query Results Count")
    creator     = models.ForeignKey(User,null=True, verbose_name="Query Creator", related_name="user_creations")
    users       = models.ManyToManyField(User)
    criteria    = models.TextField(null=True)
    snowball    = models.IntegerField(null=True, verbose_name="Snowball ID")
    step        = models.IntegerField(null=True, verbose_name="Snowball steps")
    substep     = models.IntegerField(null=True, verbose_name="Snowball query substeps")
    reftotlen   = models.IntegerField(null=True, verbose_name="Snowball Number of references")
    refdblen    = models.IntegerField(null=True, verbose_name="Snowball Number of references in the DB")
    refscraplen = models.IntegerField(null=True, verbose_name="Snowball Number of references to be scraped")
#    cittotlen   = models.IntegerField(null=True, verbose_name="Snowball Number of citations")
#    citdblen    = models.IntegerField(null=True, verbose_name="Snowball Number of citations in the DB")
    dlstat      = models.CharField(max_length=6,null=True, verbose_name="Query download status")
    technology  = models.ForeignKey('Technology', null=True)

    def __str__(self):
      return self.title

class Technology(models.Model):
    name = models.TextField(null = True, verbose_name="Technology Name")
    description = models.TextField(null=True, verbose_name="Technology Description")

    def __str__(self):
      return self.name

class SBSDocCategory(models.Model):
    name        = models.TextField(null=True, verbose_name="SBS Document Category Name")
    description = models.TextField(null=True, verbose_name="SBS Document Category Description")

    def __str__(self):
      return self.name

class Tag(models.Model):
    title = models.TextField(null=True, verbose_name="Tag Title")
    text = models.TextField(null=True, verbose_name="Tag Text")
    query = models.ForeignKey('Query',null=True, verbose_name="TagQuery")

    def __str__(self):
      return self.title

class Doc(models.Model):
    UT = models.CharField(max_length=240,db_index=True,primary_key=True, verbose_name='Document ID')
    query = models.ManyToManyField('Query')
    tag = models.ManyToManyField('Tag')
    title = models.TextField(null=True)
    content = models.TextField(null=True) 
    PY = models.IntegerField(null=True,db_index=True)
    users = models.ManyToManyField(User, through='DocOwnership')
    references = models.ManyToManyField("self", symmetrical=False)
    technology = models.ManyToManyField('Technology')
    category = models.ManyToManyField('SBSDocCategory')
    
    def __str__(self):
      return self.UT

    def ti_word_count(self):
        return len(str(self.title).split())

    def word_count(self):
        return len(str(self.content).split())

    def shingle(self):
        return set(s for s in ngrams(self.title.lower().split(),2))

class DocRel(models.Model):
    seed = models.ForeignKey(Doc, on_delete=models.CASCADE, related_name="parent")
    relation = models.IntegerField()
    text = models.TextField(null=True)
    title = models.TextField(null=True)
    au = models.TextField(null=True)
    PY = models.IntegerField(null=True)
    journal =  models.TextField(null=True)
    link = models.TextField(null=True)
    url = models.URLField(null=True) 
    doi = models.TextField(null=True)
    hasdoi = models.BooleanField(default=False)
    docmatch_q = models.BooleanField(default=False)
    timatch_q = models.BooleanField(default=False)
    indb = models.IntegerField(null=True)
    sametech = models.IntegerField(null=True)
    referent = models.ForeignKey(Doc, null=True, on_delete=models.CASCADE, related_name="document")

    class Meta:
        unique_together = ('seed', 'text',)


class Note(models.Model):
    doc = models.ForeignKey(Doc, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Notemaker")
    date = models.DateTimeField()
    text = models.TextField(null=True)
    class Meta:
        ordering = ['date']

    def __str__(self):
      return self.text

class DocOwnership(models.Model):

    UNRATED = 0
    YES = 1
    NO = 2
    MAYBE = 3
    OTHERTECH = 4

    Status = (
        (UNRATED, 'Unrated'),
        (YES, 'Yes'),
        (NO, 'No'),
        (MAYBE, 'Maybe'),
        (OTHERTECH, 'Other Technology'),
    )

    doc = models.ForeignKey(Doc, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Reviewer")
    query = models.ForeignKey(Query, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, null=True)
    relevant = models.IntegerField(
        choices=Status,
        default=0, 
        db_index=True, 
        verbose_name="Relevance"
    )
    date     = models.DateTimeField(null=True,default=timezone.now,verbose_name="Rating Date")


class DocAuthInst(models.Model):
    doc = models.ForeignKey('Doc',null=True, verbose_name="Author - Document")
    AU = models.CharField(max_length=60, db_index=True, null=True, verbose_name="Author")
    AF = models.CharField(max_length=60, db_index=True, null=True, verbose_name="Author Full Name")
    institution = models.CharField(max_length=250, db_index=True, verbose_name="Institution Name")
    position = models.IntegerField(verbose_name="Author Position")

    def __str__(self):
      return self.doc

# A simple form of the table below, just to store the dois as we parse them
class DocReferences(models.Model):
    doc = models.ForeignKey('Doc',null=True)
    refdoi = models.CharField(null=True, max_length=150, verbose_name="DOI")
    refall = models.TextField(null=True, verbose_name="All reference information") #in case we want to use this later...

    def __str__(self):
      return self.doc

#class DocCites(models.Model):
#    doc = models.ForeignKey('Doc',null=True, related_name='doc')
#    reference = models.ForeignKey('Doc',null=True, related_name='ref')

##############################################
## Article holds more WoS type information for each doc

class WoSArticle(models.Model):
    doc = models.OneToOneField(
        'Doc',
        on_delete=models.CASCADE,
        primary_key=True,
        verbose_name='Document ID'
    )
    ti = models.TextField(null=True, verbose_name="Title")
    ab = models.TextField(null=True, verbose_name="Abstract")   
    py = models.IntegerField(null=True, verbose_name="Year") 
    ar = models.CharField(null=True, max_length=100, verbose_name="Article Number") # Article number
    bn = models.CharField(null=True, max_length=100, verbose_name="ISBN") # ISBN
    bp = models.CharField(null=True, max_length=50, verbose_name="Beginning Page") # beginning page
    c1 = models.TextField(null=True, verbose_name="Author Address") # author address
    cl = models.TextField(null=True, verbose_name="Conference Location") # conf location
    ct = models.TextField(null=True, verbose_name="Conference Title") # conf title
    de = models.TextField(null=True, verbose_name="Author Keywords") # keywords - separate table?
    di = models.CharField(null=True, db_index=True, max_length=250, verbose_name="DOI") # DOI
    dt = models.CharField(null=True, max_length=50, verbose_name="Document Type") # doctype
    em = models.TextField(null=True, verbose_name="E-mail Address") #email 
    ep = models.CharField(null=True, max_length=50, verbose_name="Ending Page") # last page
    fn = models.CharField(null=True, max_length=250, verbose_name="File Name") # filename?
    fu = models.TextField(null=True, verbose_name="Funding Agency and Grant Number") #funding agency + grant number
    fx = models.TextField(null=True, verbose_name="Funding Text") # funding text
    ga = models.CharField(null=True, max_length=100, verbose_name="Document Delivery Number") # document delivery number
    ho = models.TextField(null=True, verbose_name="Conference Host") # conference host
    #ID = models.TextField() # keywords plus ??
    iss = models.CharField(null=True, max_length=100, verbose_name="Issue")
    ad = models.TextField(null=True, verbose_name="Institution (unlinked to author")
    kwp = models.TextField(null=True, verbose_name="Keywords Plus")
    j9 = models.CharField(null=True, max_length=30, verbose_name="29-Character Source Abbreviation") # 29 char source abbreviation
    ji = models.CharField(null=True, max_length=100, verbose_name="ISO Source Abbreviation") # ISO source abbrev
    la = models.CharField(null=True, max_length=100, verbose_name="Language") # Language
    nr = models.IntegerField(null=True, verbose_name="Cited Reference Count") # number of references
    pa = models.TextField(null=True, verbose_name="Publisher Address") # pub address
    pd = models.CharField(null=True, max_length=50, verbose_name="Publication Date") # pub month
    pg = models.IntegerField(null=True, verbose_name="Page Count") # page count
    pi = models.TextField(null=True, verbose_name="Publisher City") # pub city
    pt = models.CharField(null=True, max_length=50, verbose_name="Publication Type") # pub type
    pu = models.TextField(null=True, verbose_name="Publisher") # publisher
    rp = models.TextField(null=True, verbose_name="Reprint Address") # reprint address
    sc = models.TextField(null=True, verbose_name="Subject Category") # subj category
    se = models.TextField(null=True, verbose_name="Book Series Title") # book series title
    si = models.TextField(null=True, verbose_name="Special Issue") # special issue
    sn = models.CharField(null=True, max_length=80, verbose_name="ISSN") # ISSN
    so = models.CharField(null=True, max_length=250, verbose_name="Publication Name") # publication name
    sp = models.TextField(null=True, verbose_name="Conference Sponsors") # conf sponsors
    su = models.TextField(null=True, verbose_name="Supplement") # supplement
    tc = models.IntegerField(null=True, verbose_name="Times Cited") # times cited
    vl = models.CharField(null=True, max_length=50, verbose_name="Volume")
    
    def __str__(self):
      return self.ar


