<%inherit file="layout.tpl" />
% if 'logged_in' in session:
<form action="${url_for('add_entry')}" method=post class=add-entry>
  <dl>
    <dt>Title:
    <dd><input type=text size=30 name=title>
    <dt>Text:
    <dd><textarea name=text rows=5 cols=40></textarea>
    <dd><input type=submit value=Share>
  </dl>
</form>
% endif

<ul class=entries>
% if not entries:
  <li><em>Unbelievable.  No entries here so far</em></li>
% else:
  % for entry in entries:
    <li><h2>${entry['title'] | h}</h2>${entry['text']}</li>
  % endfor
% endif
</ul>
