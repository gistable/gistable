{% if post.photos %}
    {% for photo in post.photos %}
        {% if loop.index == 1 %}
        <div class="post-image">
            {% if post.type == 'link' %}
            <a href="{{ post.url }}" target="_blank">
            {% else %}
            <a href="{{ post.permalink }}">
            {% endif %}
                {% if photo %}
                <img src="{{ photo.width_600 }}" />
                {% else %}
                <img src="http://placehold.it/400x300/0eafff/ffffff.png" alt="" />
                {% endif %}
            </a>
        </div>
        {% endif %}
    {% endfor %}
{% endif %}