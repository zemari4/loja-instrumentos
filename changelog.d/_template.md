{% for section, _ in sections.items() %}
{% set underline = "#" %}
{% if sections[section] %}
{{ title_format.format(version=versiondata.public, project_date=project_date) }}

{% for category, val in definitions.items() if category in sections[section] %}
### {{ definitions[category]['name'] }}

{% for text, values in sections[section][category].items() %}
- {{ text }}
{% endfor %}

{% endfor %}
{% else %}
No significant changes.

{% endif %}
{% endfor %}
