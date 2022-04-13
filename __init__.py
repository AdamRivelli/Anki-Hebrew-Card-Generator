from anki.hooks import addHook
from aqt.utils import tooltip
from .convert import translate


def populate_fields(editor):
    editor.saveNow(lambda: _populate_fields(editor))


def _populate_fields(editor):
    url = editor.note.fields[0]
    vals = translate(url)

    for idx, val in enumerate(vals):
        editor.note.fields[idx] = val
        editor.loadNote()
    editor.note.add_tag(vals[4])
    editor.loadNote()


def add_auto_button(buttons, editor):
    auto_button = editor.addButton(
        icon=None,
        cmd="פע",
        func=populate_fields,
        tip="Download from Pealim",
        toggleable=False,
        label="",
        keys=None,
        disables=False,
    )
    buttons.append(auto_button)
    return buttons


addHook("setupEditorButtons", add_auto_button)
