..  Titling ##++::==~~--''``
    Scene ~~
    Shot --

:author: D Haynes
:date: 2016-09-13

.. character:: RAY
   :types: addisonarches.scenario.types.PrisonOfficer

   A Prison Officer. We first meet him on the day he retires.

    * Honest and concientious
    * Bruised by too many years in the service
    * Often upset by inefficiency and lack of structure

.. character:: KAREN
   :types: addisonarches.scenario.types.PrisonVisitor

   A beautician in her late forties.

    * Works in `Sandy Hair`, Leysdown-on-Sea.
    * Very organised.
    * Has always looked after |MARTIN|.

.. character:: MARTIN
   :types: addisonarches.scenario.types.Prisoner

   A small-time offender in his mid forties.

    * Can't read. Dislocated.
    * Does what he's told. Wants a quiet life.
    * Misbehaved at Standford Hill to see less of |KAREN|.

.. character:: HERO
   :types: turberfield.dialogue.types.Player

   The player character.

First positions
~~~~~~~~~~~~~~~

HM Prison Pentonville, J Wing.


Ray does the intros
-------------------

[RAY]_

    OK, there's no one else here. Looks like they've left me to supervise you on my
    own.

    |KAREN_TITLE| |KAREN_SURNAME|, you and |MARTIN_FIRSTNAME| have a longer visit today
    while we're conducting an inspection of the cell.

    |HERO_TITLE| |HERO_SURNAME|, I'm going to ask you into the Guard's Office in a moment.
    Please wait right here while I open up.

    .. property:: RAY.state turberfield.dialogue.sequences.battle_royal.types.Availability.mist

[KAREN]_

    Oooh, we can choose our own table today!

[MARTIN]_

    No, this one's ours.

.. Ray's exit means this cannot loop

.. |MARTIN_FIRSTNAME| property:: MARTIN.name.firstname
.. |HERO_TITLE| property:: HERO.name.title
.. |HERO_SURNAME| property:: HERO.name.surname
.. |KAREN_TITLE| property:: KAREN.name.title
.. |KAREN_SURNAME| property:: KAREN.name.surname
