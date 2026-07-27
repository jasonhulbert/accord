# A check-in

A check-in is human-initiated input during active work that:

- accepts an amendment or authorizes proposed or recommended work;
- provides direction or context that materially affects the agreement or
  current course; or
- directly asks about, provides feedback on, or challenges work done within the
  agreement.

An incidental or sidebar message is ordinary conversation, not a check-in. If
that is clear without consulting the work, answer normally and leave the record
alone. Invoking the `check-in` skill does not change the message's meaning.

A `completion` event ends the active work. A later message cannot be a check-in
to that agreement and is not appended to its record. If the message calls for
more work under Accord, the agent begins the conversation for a new agreement.

## Answer from the work

When the boundary depends on the work, read the agreement, record, reports,
learning notes, and actual state before classifying the message. If it does not
meet the boundary, answer normally and do not append an event.

More specific events retain their meaning. Acceptance of the initial agreement
is `start`, not `check-in`. A clear answer to an open `question` is `direction`,
not `check-in`. A direct follow-up while judgment remains open is a check-in; it
does not authorize the work that depends on that judgment.

Record a qualifying check-in with the human's words verbatim or near them.
Respond from the evidence rather than memory.

The shape of the message determines what follows:

- **An account** gets a report of what changed, what did not work, what is now
  known, and what the agent recommends next.
- **A request for counsel** gets the agent's explanation and judgment from the
  work, including relevant evidence and uncertainty.
- **A request to inspect the work** reserves judgment where the work stands.
  Make the work inspectable, report, ask for the requested judgment, and wait
  for direction.
- **New context** gets the agent's judgment about what it changes.
- **Changed terms** get counsel about cost, risk, and consequences. Record an
  accepted amendment before continuing under it.

A check-in does not halt work by itself. Work waits when the human requests
review or a halt, closes authority the agreement had left open, or leaves a
reserved question unanswered.
