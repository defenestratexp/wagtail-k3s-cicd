from django import forms
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.snippets.models import register_snippet


# Skill categories
SKILL_CATEGORIES = [
    ('cloud', 'Cloud & Infrastructure'),
    ('automation', 'Automation & CI/CD'),
    ('containers', 'Containerization & Orchestration'),
    ('monitoring', 'Monitoring & Observability'),
    ('scripting', 'Scripting & Development'),
    ('security', 'Security & Compliance'),
    ('other', 'Other'),
]


@register_snippet
class Skill(models.Model):
    """A skill on the Skills page, linked to the projects and jobs that show it in use."""
    name = models.CharField(max_length=100)
    percentage = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Unused: the proficiency bars were replaced by project and job links"
    )
    category = models.CharField(
        max_length=20,
        choices=SKILL_CATEGORIES,
        default='other'
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text="Font Awesome icon class (e.g., 'fa-aws', 'fa-docker')"
    )
    match_tags = models.CharField(
        max_length=300,
        blank=True,
        help_text="Comma-separated project technology tags that also count as this skill "
                  "(the skill name itself always counts), e.g. 'Amazon ECR, AWS Secrets Manager' for AWS"
    )
    related_jobs = models.ManyToManyField(
        'Job',
        blank=True,
        related_name='skills',
        help_text="Jobs shown for this skill when no project is tagged with it"
    )
    order = models.PositiveIntegerField(default=0)

    panels = [
        FieldPanel('name'),
        FieldPanel('category'),
        FieldPanel('icon'),
        FieldPanel('match_tags'),
        FieldPanel('related_jobs', widget=forms.CheckboxSelectMultiple),
        FieldPanel('order'),
    ]

    class Meta:
        ordering = ['category', 'order', 'name']

    def __str__(self):
        return self.name

    def tag_set(self):
        """Lower-cased project tags that count as this skill."""
        tags = [self.name] + self.match_tags.split(",")
        return {t.strip().lower() for t in tags if t.strip()}


@register_snippet
class Job(models.Model):
    """Work experience entry."""
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True)
    title = models.CharField(max_length=200)
    start_date = models.CharField(max_length=50, help_text="e.g., 'June 2024'")
    end_date = models.CharField(max_length=50, help_text="e.g., 'December 2024' or 'Present'")
    description = RichTextField(blank=True)
    bullets = RichTextField(blank=True, help_text="Key accomplishments as bullet points")
    is_contract = models.BooleanField(default=False)
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text="Font Awesome class for the home-page job row, e.g. 'fa-solid fa-car-side'"
    )
    order = models.PositiveIntegerField(default=0)

    panels = [
        FieldPanel('company'),
        FieldPanel('location'),
        FieldPanel('title'),
        MultiFieldPanel([
            FieldPanel('start_date'),
            FieldPanel('end_date'),
        ], heading="Dates"),
        FieldPanel('description'),
        FieldPanel('bullets'),
        FieldPanel('is_contract'),
        FieldPanel('icon'),
        FieldPanel('order'),
    ]

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.title} at {self.company}"

    def date_range(self):
        """'2024' when a role started and ended in the same year, else 'start - end'."""
        if self.start_date.strip() == self.end_date.strip():
            return self.start_date
        return f"{self.start_date} - {self.end_date}"


@register_snippet
class Project(models.Model):
    """Portfolio project entry."""
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200, blank=True)
    description = RichTextField()
    technologies = models.CharField(max_length=500, blank=True, help_text="Comma-separated list")
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    code_snippet = models.TextField(blank=True, help_text="Code sample (optional)")
    code_language = models.CharField(max_length=50, blank=True, help_text="e.g., 'python', 'yaml', 'bash'")
    github_url = models.URLField(blank=True)
    order = models.PositiveIntegerField(default=0)

    panels = [
        FieldPanel('title'),
        FieldPanel('company'),
        FieldPanel('description'),
        FieldPanel('technologies'),
        FieldPanel('image'),
        MultiFieldPanel([
            FieldPanel('code_snippet'),
            FieldPanel('code_language'),
        ], heading="Code Sample"),
        FieldPanel('github_url'),
        FieldPanel('order'),
    ]

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


@register_snippet
class Certification(models.Model):
    """Professional certification."""
    name = models.CharField(max_length=200)
    issuer = models.CharField(max_length=200)
    date_obtained = models.CharField(max_length=50, blank=True)
    credential_url = models.URLField(blank=True)
    badge_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    order = models.PositiveIntegerField(default=0)

    panels = [
        FieldPanel('name'),
        FieldPanel('issuer'),
        FieldPanel('date_obtained'),
        FieldPanel('credential_url'),
        FieldPanel('badge_image'),
        FieldPanel('order'),
    ]

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name


# Page models
class HomePage(Page):
    """About/Hero landing page."""

    # Hero section
    headline = models.CharField(max_length=200, default="DevOps Engineer")
    intro = RichTextField(blank=True)
    photo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    top_skills = RichTextField(
        blank=True,
        help_text="Short bulleted list of the top skills, shown under the intro"
    )

    # Contact info
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=100, blank=True)
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)

    # Resume PDF URL (external link for now)
    resume_pdf_url = models.URLField(blank=True, help_text="URL to PDF resume for download")

    # Military experience
    military_experience = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('headline'),
            FieldPanel('intro'),
            FieldPanel('top_skills'),
            FieldPanel('photo'),
        ], heading="Hero Section"),
        MultiFieldPanel([
            FieldPanel('email'),
            FieldPanel('phone'),
            FieldPanel('location'),
            FieldPanel('linkedin_url'),
            FieldPanel('github_url'),
        ], heading="Contact Information"),
        FieldPanel('resume_pdf_url'),
        FieldPanel('military_experience'),
    ]

    class Meta:
        verbose_name = "Home Page"

    subpage_types = ['home.SkillsPage', 'home.ExperiencePage', 'home.ProjectsPage', 'home.ContactPage']

    def job_icons(self):
        """Jobs that have an icon, each linked to its entry on the Experience page."""
        experience = ExperiencePage.objects.live().first()
        base = experience.url if experience else ''
        jobs = Job.objects.exclude(icon='').order_by('is_contract', 'order')
        # "\u200b" after a slash lets "Mphasis/Stelligent" wrap at the slash, not mid-word
        return [{'job': j, 'url': f"{base}#job-{j.id}", 'label': j.company.replace('/', '/\u200b')}
                for j in jobs]

    def project_icons(self):
        """Live project pages that have an icon, in their usual order."""
        return ProjectPage.objects.live().exclude(icon='').order_by('order')

    def projects_url(self):
        page = ProjectsPage.objects.live().first()
        return page.url if page else ''


class SkillsPage(Page):
    """Skills page: each skill expands to the projects or jobs that show it."""

    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]

    class Meta:
        verbose_name = "Skills Page"

    parent_page_types = ['home.HomePage']
    subpage_types = []

    def get_skills_by_category(self):
        """Skills grouped by category, each with the projects (or, failing that, jobs) that show it.

        A project matches a skill when one of its technology tags equals the skill
        name or one of the skill's match_tags. Jobs are only listed for skills that
        no live project covers.
        """
        projects = [(p, {t.lower() for t in p.tech_list()})
                    for p in ProjectPage.objects.live().order_by('order')]
        experience = ExperiencePage.objects.live().first()
        skills = Skill.objects.prefetch_related('related_jobs')
        categories = {}
        for category_code, category_name in SKILL_CATEGORIES:
            entries = []
            for skill in skills:
                if skill.category != category_code:
                    continue
                tags = skill.tag_set()
                matched = [p for p, ptags in projects if tags & ptags]
                jobs = [] if matched else [
                    {'job': j, 'url': f"{experience.url}#job-{j.id}" if experience else ''}
                    for j in skill.related_jobs.all()
                ]
                entries.append({'skill': skill, 'projects': matched, 'jobs': jobs})
            if entries:
                categories[category_name] = entries
        return categories


class ExperiencePage(Page):
    """Work experience timeline page."""

    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]

    class Meta:
        verbose_name = "Experience Page"

    parent_page_types = ['home.HomePage']
    subpage_types = []

    def get_jobs(self):
        """Return all jobs ordered."""
        return Job.objects.filter(is_contract=False)

    def get_contracts(self):
        """Return contract/project work."""
        return Job.objects.filter(is_contract=True)


class ProjectsPage(Page):
    """Portfolio projects page."""

    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]

    class Meta:
        verbose_name = "Projects Page"

    parent_page_types = ['home.HomePage']
    subpage_types = ['home.ProjectPage']

    def get_projects(self):
        """Return all child project pages."""
        return ProjectPage.objects.live().child_of(self).order_by('order')

    def get_certifications(self):
        """Return all certifications."""
        return Certification.objects.all()


class ProjectPage(Page):
    """Individual project detail page."""

    # Card display fields
    summary = models.TextField(help_text="Short description for project card (1-2 sentences)")
    thumbnail = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Image shown on project card"
    )
    technologies = models.CharField(max_length=500, blank=True, help_text="Comma-separated list for card badges")
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text="Font Awesome class for the home-page project row, e.g. 'fa-solid fa-radio'"
    )
    short_name = models.CharField(
        max_length=40,
        blank=True,
        help_text="Short label for the home-page project row (defaults to the page title)"
    )
    order = models.PositiveIntegerField(default=0)

    # Detail page fields
    challenge = RichTextField(blank=True, help_text="The problem or need that was addressed")
    solution = RichTextField(blank=True, help_text="How the project solved the challenge")
    details = RichTextField(blank=True, help_text="Technical implementation details")
    diagram = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Architecture or flow diagram"
    )
    diagram_caption = models.CharField(max_length=300, blank=True)

    # Optional extras
    github_url = models.URLField(blank=True)
    demo_url = models.URLField(blank=True)
    code_snippet = models.TextField(blank=True, help_text="Optional code sample")
    code_language = models.CharField(max_length=50, blank=True, help_text="e.g., 'python', 'yaml', 'bash'")

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('summary'),
            FieldPanel('thumbnail'),
            FieldPanel('technologies'),
            FieldPanel('icon'),
            FieldPanel('short_name'),
            FieldPanel('order'),
        ], heading="Card Display"),
        MultiFieldPanel([
            FieldPanel('challenge'),
            FieldPanel('solution'),
            FieldPanel('details'),
        ], heading="Project Details"),
        MultiFieldPanel([
            FieldPanel('diagram'),
            FieldPanel('diagram_caption'),
        ], heading="Diagram"),
        MultiFieldPanel([
            FieldPanel('github_url'),
            FieldPanel('demo_url'),
            FieldPanel('code_snippet'),
            FieldPanel('code_language'),
        ], heading="Optional"),
    ]

    def row_label(self):
        return self.short_name or self.title

    def tech_list(self):
        """Technologies as a list, split on commas so multi-word names stay whole."""
        return [t.strip() for t in self.technologies.split(",") if t.strip()]

    class Meta:
        verbose_name = "Project Page"
        ordering = ['order']

    parent_page_types = ['home.ProjectsPage']
    subpage_types = []


class ContactPage(Page):
    """Contact page with Calendly integration."""

    intro = RichTextField(blank=True)
    calendly_url = models.URLField(blank=True, help_text="Calendly scheduling link")
    calendly_text = models.CharField(max_length=200, default="Schedule a Meeting")
    email = models.EmailField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        MultiFieldPanel([
            FieldPanel('calendly_url'),
            FieldPanel('calendly_text'),
        ], heading="Calendly"),
        FieldPanel('email'),
    ]

    class Meta:
        verbose_name = "Contact Page"

    parent_page_types = ['home.HomePage']
    subpage_types = []
