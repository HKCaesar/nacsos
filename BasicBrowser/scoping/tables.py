import django_tables2 as tables
from django_tables2.utils import A
from .models import *
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from tmv_app.models import *
from .filters import *
import django_filters

#from .urls import urlpatterns


class ProjectTable(tables.Table):
    id = tables.LinkColumn('scoping:project', args=[A('pk')])
    queries = tables.LinkColumn('scoping:queries', args=[A('pk')])
    tms = tables.LinkColumn('tmv_app:runs', args=[A('pk')])
    class Meta:
        model = Project
        fields = ('id','title','description','role','queries','docs','tms')

class FloatColumn(tables.Column):
    # def __init__(self, **kwargs):
    #     if 'digits' in kwargs:
    #         self.digits = kwargs['digits']
    #     else:
    #         self.digits = 2
    def render(self, value):
        return round(value,3)

class TopicTable(tables.Table):
    run_id = tables.LinkColumn('tmv_app:topics', args=[A('pk')])
    error = FloatColumn()
    coherence = FloatColumn()
    # queries = tables.LinkColumn('scoping:queries', args=[A('pk')])
    # tms = tables.LinkColumn('tmv_app:runs', args=[A('pk')])
    #id = tables.LinkColumn('scoping:project', args=[A('pk')])
    # startit = tables.LinkColumn(
    #     'scoping:run_model',
    #     text='Start',
    #     args=[A('pk')]
    # )
    class Meta:
        model = RunStats
        fields = (
            'run_id','method',
            'start','status',
            'K','alpha',
            'min_freq','max_df',
            'error','coherence',
            'psearch'
        )#'startit')

#from .urls import urlpatterns

class DocParTable(tables.Table):

    document = tables.Column(
        accessor='doc.title',
        verbose_name='Document'
    )

    class Meta:
        model = DocPar
        fields = (
            'document','text',
        )
        template_name = 'django_tables2/bootstrap.html'
        attrs = {'class': 'table'}


class FilteredDocPar(SingleTableMixin, FilterView):
    table_class = DocParTable
    model = DocPar
    template_name = 'par_manager.html'

    filterset_class = DocParFilter

class TagTable(tables.Table):
    class Meta:
        model = Tag
        fields = (
            'title',
        )
