..  Titling
    ##++::==~~--''``

Remote Procedure Calls
======================

.. seqdiag::
   :alt: Enrolment sequence

   seqdiag {
    default_fontsize = 14;
    "User"; "Initiator"; "Processor";
    "User" -> "Initiator" [leftnote="GET /session?pause=&dwell="]{
        "Initiator" -> "Processor" [leftnote="GET /dialogue"];
        "Processor" -> "Processor" [note="Performer.run(react=False)"];
        "Initiator" <- "Processor" [label="json"];
        "Initiator" -> "Initiator" [note="Load events from JSON"];
        "Initiator" -> "Initiator" [note="Calculate page refresh (to audio or end)."];
    }
   }


