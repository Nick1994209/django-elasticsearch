from datetime import datetime

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from elasticsearch import ElasticsearchException

from .. import elasticsearch_analysis as es_analysis
from django_elasticsearch.models import EsIndexable
from django_elasticsearch.serializers import EsJsonSerializer


class TestSerializer(EsJsonSerializer):
    # Note: i want this field to be null instead of u''
    def serialize_email(self, instance, field_name):
        val = getattr(instance, field_name)
        if val == u'':
            return None
        return val

    def serialize_date_joined_exp(self, instance, field_name):
        # abstract
        return {'iso': instance.date_joined.isoformat(),
                'timestamp': instance.date_joined.strftime('%s.%f')}


class TestModel(User, EsIndexable):
    class Elasticsearch(EsIndexable.Elasticsearch):
        index = 'django-test'
        doc_type = 'test-doc-type'
        mappings = {
            "username": {"index": "not_analyzed"},
            "date_joined_exp": {"type": "object"}
        }
        serializer_class = TestSerializer

    class Meta:
        proxy = True
        ordering = ('id',)


class Dummy(models.Model):
    foo = models.CharField(max_length=256, null=True)


class Test2Serializer(EsJsonSerializer):
    def serialize_type_datetimefield(self, instance, field_name):
        d = getattr(instance, field_name)
        # a rather typical api output
        return {
            'iso': d and d.isoformat(),
            'date': d and d.date().isoformat(),
            'time': d and d.time().isoformat()[:5]
        }

    def deserialize_type_datetimefield(self, instance, field_name):
        return datetime.strptime(instance.get(field_name)['iso'],
                                 '%Y-%m-%dT%H:%M:%S.%f')

    def serialize_abstract_method(self, instance, field_name):
        return 'woot'

    def serialize_bigint(self, instance, field_name):
        return 42

    def deserialize_bigint(self, source, field_name):
        return 45


class Test2Model(EsIndexable):
    # string
    char = models.CharField(max_length=256, null=True)
    text = models.TextField(null=True)
    email = models.EmailField(null=True)
    filef = models.FileField(null=True, upload_to='f/')
    # img = models.ImageField(null=True)  # would need pillow
    filepf = models.FilePathField(null=True)
    ipaddr = models.IPAddressField(null=True)
    genipaddr = models.GenericIPAddressField(null=True)
    slug = models.SlugField(null=True)
    url = models.URLField(null=True)

    # numeric
    intf = models.IntegerField(null=True)
    bigint = models.BigIntegerField(null=True)
    intlist = models.CommaSeparatedIntegerField(max_length=256, null=True)
    floatf = models.FloatField(null=True)
    dec = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    posint = models.PositiveIntegerField(null=True)
    smint = models.SmallIntegerField(null=True)
    possmint = models.PositiveSmallIntegerField(null=True)

    # dj1.8
    # binary = models.BinaryField()

    # bool
    boolf = models.BooleanField(null=False, default=True)
    nullboolf = models.NullBooleanField(null=True)

    # datetime
    datef = models.DateField(null=True)
    datetf = models.DateTimeField(null=True, auto_now_add=True)
    timef = models.TimeField(null=True)

    # related
    fk = models.ForeignKey(Dummy, null=True, related_name="tofk")
    oto = models.OneToOneField(Dummy, null=True, related_name="toto")
    fkself = models.ForeignKey('self', null=True, related_name="toselffk")  # a bit of a special case
    mtm = models.ManyToManyField(Dummy, related_name="tomtm")

    class Elasticsearch(EsIndexable.Elasticsearch):
        index = 'django-test'
        doc_type = 'test-doc-type'
        serializer_class = Test2Serializer
        # Note: we need to specify this field since the value returned
        # by the serializer does not correspond to it's default mapping
        # see: Test2Serializer.serialize_type_datetimefield
        mappings = {'datetf': {'type': 'object'}}

    @property
    def abstract_prop(self):
        return 'weez'


class News(EsIndexable, models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )
    img = models.ForeignKey(
        'Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    is_published = models.BooleanField(
        default=False,
    )
    is_deleted = models.BooleanField(default=False)
    publish_date = models.DateTimeField(
        default=datetime.now,
    )
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    modified = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')
    is_main = models.BooleanField(default=False, verbose_name='Главная', editable=False)

    class Elasticsearch(EsIndexable.Elasticsearch):
        fields = ('id', 'title', 'stripped_content', 'label', 'is_published')
        analysis = es_analysis.analysis
        mappings = {
            'stripped_content': {
                'analyzer': es_analysis.ngram_analyzer,
                'search_analyzer': es_analysis.standard_analyzer,
            },
            'title': {
                'analyzer': es_analysis.ngram_analyzer,
                'search_analyzer': es_analysis.standard_analyzer,
            },
        }
        fuzziness = 2

    @classmethod
    def search(cls, query, limit=10):

        try:
            news_from_es = cls.es.search(query).filter(is_published=True)[:limit]
        except ElasticsearchException:
            print('Error searching news in elastic for query %s', query)
            return []
        news_ids = [article['id'] for article in news_from_es]
        news = cls.objects.filter(id__in=news_ids).select_related('author', 'img', 'label')
        ordered_news = sorted(news, key=lambda article: news_ids.index(article.id))
        return news
