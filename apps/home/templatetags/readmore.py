from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe
from apps.home.models import *
register = template.Library()

import re

readmore_showscript = ''.join([
"this.parentNode.style.display='none';",
"this.parentNode.parentNode.getElementsByClassName('more')[0].style.display='inline';",
"return false;",
])

#@register.filter
@register.simple_tag
def readmore2(txt,  showwords=0,id=0):
    global readmore_showscript
    words = re.split(r' ', escape(txt))

    if len(words) <= showwords:
        return txt

    # wrap the more part
    words.insert(showwords, '<span class="more_'+str(id)+'" style="display:none;">')
    words.append('</span>')

    # insert the readmore part
    words.insert(showwords, '<span class="readmore">... <a href="#" onclick="')
    words.insert(showwords+1, ''.join([
"this.parentNode.style.display='none';",
"this.parentNode.parentNode.getElementsByClassName('more_"+str(id)+"')[0].style.display='inline';",
"return false;",
]))
    words.insert(showwords+2, '">read more</a>')
    words.insert(showwords+3, '</span>')
  
    # Wrap with <p>
    words.insert(0, '<p class="shadow-none p-3 mb-5 bg-light rounded" >')
    words.append('</p>')

    return mark_safe(' '.join(words))

readmore2.is_safe = True



@register.simple_tag
def readmore(text, url):
    return mark_safe(f'<p>{text} <a href="{url}">Read more</a></p>')


@register.simple_tag
def get_news_file(pk):
    objects = NewsPhoto.objects.filter(news=pk).first()
    
    return objects.image.url if objects.image  else '' 


@register.inclusion_tag('blogs/news/tags/modal.html')
def news_files(pk):
    objects = NewsPhoto.objects.filter(news=pk)
    
    return {'objects': objects, 'pk':pk}

  

  
@register.inclusion_tag('blogs/news/tags/modal.html')
def events_files(pk):
    objects = EventPhoto.objects.filter(event=pk)
    
    return {'objects': objects, 'pk':pk}
