from six import u

from django.db import models
from django.utils.text import get_text_list
from django.utils.translation import gettext_lazy as _

from modelcluster.models import ClusterableModel
from modelcluster.fields import ParentalKey

from robots.panels import WrappedInlinepanel


from wagtail.models import Site
from wagtail.admin.panels import FieldPanel


class BaseUrl(models.Model):
    """
    Defines a URL pattern for use with a robot exclusion rule. It's
    case-sensitive and exact, e.g., "/admin" and "/admin/" are different URLs.
    """
    pattern = models.CharField(
        _('pattern'),
        max_length=255,
        help_text=_(
            "Case-sensitive. A missing trailing slash does al"
            "so match to files which start with the name of "
            "the pattern, e.g., '/admin' matches /admin.html "
            "too. Some major search engines allow an asterisk"
            " (*) as a wildcard and a dollar sign ($) to "
            "match the end of the URL, e.g., '/*.jpg$'."))

    class Meta:
        verbose_name = _('url')
        verbose_name_plural = _('urls')
        abstract = True

    def __str__(self):
        return u("%s") % self.pattern

    def save(self, *args, **kwargs):
        if not self.pattern.startswith('/'):
            self.pattern = '/' + self.pattern
        super(BaseUrl, self).save(*args, **kwargs)

    content_panels = [
        FieldPanel('pattern')
    ]


class AllowedUrl(BaseUrl):
    rule = ParentalKey(
        'robots.Rule',
        related_name='allowed')


class DisallowedUrl(BaseUrl):
    rule = ParentalKey(
        'robots.Rule',
        related_name='disallowed')


class Rule(ClusterableModel):
    """
    Defines an abstract rule which is used to respond to crawling web robots,
    using the robot exclusion standard, a.k.a. robots.txt. It allows or
    disallows the robot identified by its user agent to access the given URLs.
    The Site contrib app is used to enable multiple robots.txt per instance.
    """
    robot = models.CharField(
        _('robot'),
        max_length=255,
        help_text=_(
            "This should be a user agent string like "
            "'Googlebot'. Enter an asterisk (*) for all "
            "user agents. For a full list look at the "
            "<a target=_blank href='"
            "http://www.robotstxt.org/db.html"
            "'> database of Web Robots</a>."))

    sites = models.ManyToManyField(
        Site,
        blank=True,
        related_name="sites",
        verbose_name=_('sites'),
        help_text=_(
            "The sites which these rules apply to. If none selected, "
            "will apply to all sites. CTRL+Click to deselect."))

    crawl_delay = models.DecimalField(
        _('crawl delay'),
        blank=True, null=True, max_digits=3, decimal_places=1,
        help_text=_(
            "Between 0.1 and 99.0. This field is supported by some search "
            "engines and defines the delay between successive crawler "
            "accesses in seconds. If the crawler rate is a problem for your "
            "server, you can set the delay up to 5 or 10 or a comfortable "
            "value for your server, but it's suggested to start with small "
            "values (0.5-1), and increase as needed to an acceptable value "
            "for your server. Larger delay values add more delay between "
            "successive crawl accesses and decrease the maximum crawl rate to "
            "your web server."))

    panels = [
        FieldPanel('robot'),
        FieldPanel('sites'),
        WrappedInlinepanel(
            'allowed', heading="Allowed Urls",
            label="Add new allowed url",
            card_header_from_field='pattern',
            new_card_header_text="New allowed url"),
        WrappedInlinepanel(
            'disallowed', heading="Disallowed Urls",
            label="Add new disallowed url",
            card_header_from_field='pattern',
            new_card_header_text="New allowed url"),
        FieldPanel('crawl_delay'),
    ]

    class Meta:
        verbose_name = _('robots.txt rule')
        verbose_name_plural = _('robots.txt rules')

    def __str__(self):
        return u("%s") % self.robot

    def allowed_urls(self):
        return get_text_list(list(self.allowed.all()), _('and'))
    allowed_urls.short_description = _('allowed')

    def disallowed_urls(self):
        return get_text_list(list(self.disallowed.all()), _('and'))
    disallowed_urls.short_description = _('disallowed')
