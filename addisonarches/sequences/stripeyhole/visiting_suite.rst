..  vim: textwidth=84

..  Titling ##++::==~~--''``
    Scene ~~
    Shot --

:author: D Haynes
:date: 2016-09-13

.. |HERO| property:: HERO.name.firstname
.. |KAREN| property:: KAREN.name.firstname
.. |MARTIN| property:: MARTIN.name.firstname

.. entity:: KAREN
   :types: addisonarches.scenario.types.PrisonVisitor

   A beautician in her late forties.

    * Works in `Sandy Hair`, Leysdown-on-Sea.
    * Very organised.
    * Has always looked after |MARTIN|.
    * Grateful to |HERO| for being good cellmate. Worried about what comes next.

.. entity:: MARTIN
   :types: addisonarches.scenario.types.Prisoner

   A small-time offender in his mid forties.

    * Can't read. Dislocated.
    * Does what he's told. Wants a quiet life.
    * Misbehaved at Standford Hill to see less of |KAREN|.

.. entity:: HERO
   :types: turberfield.dialogue.types.Player

   The player entity.

.. entity:: KEYS
   :types: addisonarches.scenario.types.Keys

   The keys to Addison Arches.


In the Visiting Suite
~~~~~~~~~~~~~~~~~~~~~


HM Prison Pentonville, J Wing.


Karen talks of the journey
--------------------------


[KAREN]_

    I don't like visiting time so early. There's traffic now on the M2.

[MARTIN]_

    Yeah.

[KAREN]_

    But it's not so bad later on.

[MARTIN]_

    No.

[KAREN]_

    Mid morning's okay. I sometimes go with the girls for lunch at Farthing Corner.

    Which is nice.

[MARTIN]_

    Oh.

[KAREN]_

    I really don't know why they had to move you up here. Standford Hill was much
    easier.

[MARTIN]_

    Yeah, easier, but...

[KAREN]_

    And this place is full of hard nuts. Why did they think you belonged here? You were
    close to coming out, too.

[MARTIN]_

    No, it's...

    A shame.

Karen talks of her work
-----------------------


[KAREN]_

    Mandy left finally, and we had a move round.
    So I've got the chair by the window now.

[MARTIN]_

    Yeah.

[KAREN]_

    Which I like, but in the summer you get the sun right on you.

    When the drier's on that's too much.

[MARTIN]_

    Yeah.

[KAREN]_

    And wintertime the cold comes straight through the glass.

    So I have my cardie.

[MARTIN]_

    Oh.

[KAREN]_

    And you get the wind through the door.

[MARTIN]_

    Yep.

[KAREN]_

    And I keep my bag in the back and it's further away now and I can't see it from
    where I am.

[MARTIN]_

    No.


[KAREN]_

    But I do like it.

    Mandy had it all the time she was there so fair's fair.


[MARTIN]_

    . . .

    So now you're working at the fair?


[KAREN]_

    No, |MARTIN| I work at Sandy Hair.

    Next to the fair.

[MARTIN]_

    I thought you said you worked at the fair.

    Did you get sacked from the cleaning?

[KAREN]_

    No, I still do the cleaning.

Karen talks of the keys
-----------------------


[KAREN]_

    Which reminds me. What are these for?

.. property:: KEYS.presence turberfield.dialogue.types.Presence.shine

[MARTIN]_

    What?

    Don't know.

    But don't wave them around.

[KAREN]_

    They came in the post the other day.

    With some documents. They were addressed to you.

[MARTIN]_

    It's nothing. Shut up about it.

[MARTIN]_

    The big one is for the front doors. Silver one is the office key.
    And this one opens the padlock on the cage.

    Flog as much of that gear as you can, but don't get caught with
    it, right?

.. memory:: turberfield.dialogue.types.Ownership.acquired
   :subject: HERO
   :object: KEYS

   The keys to 18A Addison Arches. Big one is for the front doors.
   Padlock for the cage. Key to the office.


[MARTIN]_

    If you see any faces sniffing around there, just tell 'em you're
    looking after it for Frankie Drum.

    They'll get the idea.

.. memory:: turberfield.dialogue.types.Vocabulary.prompted
   :subject: MARTIN
   :object: HERO

   This place belongs to Frankie Drum. Now go away.

