from turberfield.dialogue.model import SceneScript

from addisonarches.sequences.stripeyhole.interludes import default
from addisonarches.sequences.stripeyhole.interludes import stop

__doc__ = """
The very first scripted scenes to appear in Addison Arches.

"""

contents = SceneScript.Folder(
    "addisonarches.sequences.stripeyhole",
    __doc__,
    ["first_positions.rst", "visiting_suite.rst", "guards_office.rst"],
    [default, default, stop]
)
