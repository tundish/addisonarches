from turberfield.dialogue.model import SceneScript

from addisonarches.sequences.stripeyhole.interludes import default

__doc__ = """
The very first scripted scenes to appear in Addison Arches.

"""

contents = SceneScript.Folder(
    "addisonarches.sequences.stripeyhole",
    __doc__,
    ["first_positions.rst", "visiting_suite.rst"],
    [default, default]
)
