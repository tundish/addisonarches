..  Titling ##++::==~~--''``
    Scene ~~
    Shot --

:author: D Haynes
:date: 2016-09-13

.. |HERO| property:: HERO.name.firstname

.. entity:: RAY
   :types: addisonarches.scenario.types.PrisonOfficer

.. entity:: MARTIN
   :types: addisonarches.scenario.types.Prisoner

.. entity:: HERO
   :types: turberfield.dialogue.types.Player

   The player entity.

.. entity:: B107
   :types: addisonarches.scenario.types.FormB107

   A personality profile of |HERO|.



Guards' Office
~~~~~~~~~~~~~~

HM Prison Pentonville, J Wing.

Ray complains about the service
-------------------------------

.. property:: MARTIN.presence turberfield.dialogue.types.Presence.invisible


[RAY]_

    Dear oh dear, what a mess today. I'm the only one who tidies this place up.

    No-one replaces the stationery here you know. I had to bring in a load of rubber bands
    this morning from home.

    The only thing we've got left here is pens. Ironically no one seems to steal those.

Ray says goodbye
----------------


[RAY]_

    Well, now, let's have you on your way.

.. property:: B107.presence turberfield.dialogue.types.Presence.shine

[RAY]_

    It isn't usual to read a form B107 to its subject, |HERO_TITLE| |HERO_SURNAME|, but
    it looks like you've been playing it straight.

    I can see you have a difficult family background. Very easy to find yourself in prison
    the first time.

    But I'd like to say, I've been impressed by your influence on |MARTIN_FIRSTNAME| |MARTIN_SURNAME|.
    His literacy is very much improved. And he's been practicing his handwriting too, I understand.

    Well done for making it so far.

    Take every opportunity you find out there.


.. |HERO_TITLE| property:: HERO.name.title
.. |HERO_SURNAME| property:: HERO.name.surname
.. |MARTIN_FIRSTNAME| property:: MARTIN.name.firstname
.. |MARTIN_SURNAME| property:: MARTIN.name.surname
