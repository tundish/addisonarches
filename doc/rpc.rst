..  Titling
    ##++::==~~--''``

Remote Procedure Calls
======================

.. seqdiag::
   :alt: Enrolment sequence

   seqdiag {
    default_fontsize = 14;
    "Supervisor"; "Sender"; "POA"; "Receiver";
    "Supervisor" ->> "Sender" [leftnote="Launch"]{
        "Sender" -> "POA" [note="Search for receiver flow"];
        "Sender" <- "POA";
    }
    "Supervisor" ->> "Receiver" [leftnote="Launch"]{
        "Receiver" -> "POA" [note="Establish RX role"];
        "Receiver" <-- "POA";
    }
    "Supervisor" <<- "Receiver";
    "Sender" -> "POA" [note="Search for receiver flow"];
    "Sender" <- "POA" [label="flow"];
    "Sender" -> "POA" [note="Establish TX role"];
    "Sender" <-- "POA";
    "Sender" ->> "Receiver" [diagonal, label="msg"];
    "Sender" -> "POA" [note="Update TX role"];
    "Sender" <-- "POA";
    "Receiver" -> "POA" [note="Update RX role"];
    "Receiver" <-- "POA";
   }


