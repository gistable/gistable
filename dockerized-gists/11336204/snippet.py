def import_wp(language):
    from django.template.defaultfilters import truncatewords_html
    from cms.api import add_plugin
    from wordpress.models import Post as WPost
    from djangocms_blog.models import Post, BlogCategory
    from django.contrib.auth.models import User


    for post in WPost.objects.published():
        print post.title
        author = None
        users = User.objects.filter(username=post.author.login)
        if users.exists():
            author = users[0]
        if not author:
            users = User.objects.filter(email=post.author.email)
            if users.exists():
                author = users[0]
        if not author:
            author = User.objects.get(pk=1)
        new_post = Post()
        new_post.set_current_language(language)
        new_post.title = post.title
        new_post.slug = post.slug
        new_post.abstract = truncatewords_html(post.content, 20)
        new_post.date_created = post.post_date
        new_post.date_published = post.post_date
        new_post.date_modified = post.modified
        new_post.save()
        add_plugin(new_post.content, 'TextPlugin', language, body=post.content)
        if author:
            new_post.author = author
        for cat in post.categories():
            try:
                category = BlogCategory.objects.language(language).get(translations__name=cat.name)
            except BlogCategory.DoesNotExist:
                category = BlogCategory()
                category.set_current_language(language)
                category.name = cat.name
                category.save()
            new_post.categories.add(category.pk)
        if post.tags():
            for tag in post.tags():
                new_post.tags.add(tag.name)
        new_post.save()