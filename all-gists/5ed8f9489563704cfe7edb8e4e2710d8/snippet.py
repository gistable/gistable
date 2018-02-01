<ol class="breadcrumb">
    {% set crumbs = [] %}
    {% set current = {'crumb': this} %}
    {% for i in this._path.split("/") %}
        {% if current.crumb is not none %}
            {% if crumbs.insert(0, current.crumb) %}{% endif %}
            {% if current.update({"crumb": current.crumb.parent}) %}{% endif %}
        {% endif %}
    {% endfor %}
    {% for crumb in crumbs %}
        {% if this._path == crumb._path %}
            <li class="active">{{ crumb.title }}</li>
        {% else %}
            <li><a href="{{ crumb|url }}">{{ crumb.title }}</a></li>
        {% endif %}
    {% endfor %}
</ol>